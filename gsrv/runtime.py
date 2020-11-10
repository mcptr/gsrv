from gsrv.dtypes import (  # noqa
    Base,
    Field,
    Game,
    IncomingMessage,
    OutgoingMessage,
    ErrorMessage,
    LogMessage,

    MessageNames,
)
from gsrv.connection import Connection

import websockets
import asyncio
import logging
import uuid
import typing as T


class _GameDriver:
    pass


class _RT(Base):
    rt_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    pgpool: T.Any
    redis: T.Any
    games: T.Dict[str, _GameDriver] = Field(default_factory=dict)
    stop_ev: asyncio.Event = Field(default_factory=asyncio.Event)
    logger: T.Optional[T.Any] = None
    _lck_games = asyncio.Lock()

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.get_logger(self.__class__.__name__)

    def get_logger(self, name):
        return logging.getLogger(name)

    def is_running(self):
        return not self.stop_ev.is_set()

    def stop(self):
        self.stop_ev.set()


class GameDriver(_GameDriver):
    def __init__(self, rt: _RT, game: Game, task: T.Awaitable):
        self.logger = rt.get_logger(self.__class__.__name__)
        self.rt = rt
        self.game = game
        self.task = task
        self.all_clients: T.Dict[str, T.Tuple[Connection, T.Awaitable]] = {}
        self._lck_players = asyncio.Lock()

    async def add_connection(self, connection) -> None:
        self.logger.info(connection)
        c_id = str(connection)
        if c_id not in self.all_clients:
            print("ADD_CONNECTION", connection)
            self.all_clients[c_id] = (
                connection,
                asyncio.create_task(self.handle_client_session(connection))
            )
            await self.broadcast(LogMessage(data="%s connected" % c_id).json())

    async def remove_connection(self, connection: Connection) -> None:
        self.logger.info(connection)
        c_id = str(connection)
        if c_id in self.all_clients:
            (c, task) = self.all_clients.pop(c_id)
            task.cancel()
            await task
            print("AWAIT", c)

            print("REMOV", connection)
            if c_id in self.game.players:
                await self.remove_player(connection)

            await self.broadcast(
                LogMessage(data="%s disconnected" % c_id).json())

            await c.close()

    async def add_player(self, connection: Connection) -> None:
        self.logger.info(connection)
        ok = False
        async with self._lck_players:
            ok = self.game.add_player(str(connection))
        print("ADDDDDDDD PLAYER OK?", ok)
        if ok:
            msg = LogMessage(
                name=MessageNames.GAME_JOIN,
                data=connection.username
            )
            await self.broadcast(msg.json())
        else:
            await connection.send(
                ErrorMessage(name=MessageNames.GAME_JOIN,
                             data="Already a player.")
            )

    async def remove_player(self, connection: Connection) -> None:
        self.logger.info(connection)
        async with self._lck_players:
            self.game.remove_player(str(connection))

    async def broadcast(self, msg) -> None:
        clients = list(self.all_clients.items())
        for c_id, (c, *_) in clients:
            try:
                await c.send(msg)
            except websockets.WebSocketException:
                await self.remove_connection(c)

    async def handle_client_session(self, connection: Connection):
        print("HANDLE SESSION", connection)
        try:
            async for msg in connection.ws:
                msg = IncomingMessage.loads(msg)
                await self.on_message(msg, connection)
        except Exception as e:
            self.logger.exception(e)

        await self.remove_connection(connection)
        self.logger.info("Finished: %s", connection)

    async def on_message(self,
                         msg: IncomingMessage,
                         connection: Connection) -> None:
        if msg.name == MessageNames.GAME_JOIN:
            print(msg)
            await self.add_player(connection)

    async def start(self) -> None:
        await self.game.start()


class RT(_RT):
    async def add_game(self, game: Game, task: asyncio.Task):
        async with self._lck_games:
            self.games[str(game.game_id)] = GameDriver(
                rt=self,
                game=game,
                task=task,
            )

    async def remove_game(self, game_id: uuid.UUID):
        gr = self.games[str(game_id)]
        self.logger.info("%s, %s", game_id, gr.game.state.is_cancelled)
        await gr.task

        async with self._lck_games:
            del self.games[str(game_id)]
