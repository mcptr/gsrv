from gcli.dtypes import (
    MessageNames,
    IncomingMessage,
    OutgoingMessage,
    Game,
    WebSocket,
)

import websockets
import asyncio
import logging
import abc
import typing as T
import uuid

from urllib.parse import urljoin


class _BaseClient(abc.ABC):
    def __init__(self,
                 url: str,
                 *,
                 headers: T.Optional[T.Dict[str, T.Any]] = None,
                 stop_ev: T.Optional[asyncio.Event] = None,
                 **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.url = url
        self.headers = headers
        self.stop_ev = (stop_ev or asyncio.Event())
        self.tasks: T.List[T.Awaitable] = []
        self._is_finished = False

    @abc.abstractmethod
    async def on_message(self,
                         msg: IncomingMessage,
                         ws: WebSocket):
        ...

    async def on_setup(self):
        """Before connection"""
        ...

    async def on_connection_made(self, ws: WebSocket):
        """Once the connection is established"""
        self.tasks.extend([
            asyncio.create_task(self.consume_messages(ws)),
        ])

    async def on_shutdown(self):
        """Before exit"""
        ...

    async def consume_messages(self, ws):
        while not self.stop_ev.is_set() and not self._is_finished:
            try:
                data = await asyncio.wait_for(ws.recv(), timeout=2)
                msg = IncomingMessage.loads(data, auto_cast=True)
                await self.on_message(msg, ws)
            except asyncio.TimeoutError:
                continue
            except (websockets.ConnectionClosed,
                    websockets.ConnectionClosedOK) as e:
                self.logger.debug("Disconnected")
                break
            except (websockets.WebSocketException, Exception) as e:
                self.logger.exception(e)
                break

        await ws.close()
        self._is_finished = True

    async def send_command(self, ws, msg_name, intval_sec=1):
        while not self.stop_ev.is_set() and not self._is_finished:
            try:
                await ws.send(OutgoingMessage(name=msg_name).json())
                await asyncio.wait_for(self.stop_ev.wait(), timeout=intval_sec)
            except asyncio.TimeoutError:
                pass
            except (websockets.WebSocketException) as e:
                self.logger.error(e)
                break
            except Exception as e:
                self.logger.exception(e)
                break

    async def stop(self):
        self.stop_ev.set()

    async def start(self):
        self.logger.debug(self.url)

        await self.on_setup()
        try:
            async with websockets.connect(self.url,
                                          extra_headers=self.headers) as ws:
                await self.on_connection_made(ws)
                await asyncio.gather(*self.tasks)
        except (websockets.ConnectionClosed,
                websockets.ConnectionClosedOK):
            pass
        except (websockets.WebSocketException,
                ConnectionRefusedError,
                ConnectionResetError,
                Exception) as e:
            self.logger.error(e)
        finally:
            await self.on_shutdown()
            self.logger.debug("Exiting")


class GameClient(_BaseClient):
    def __init__(self, game_id: uuid.UUID, *args, **kwargs):
        self.game_id = game_id
        super().__init__(*args, **kwargs)

    async def on_connection_made(self, ws: WebSocket):
        await super().on_connection_made(ws)
        om = OutgoingMessage(name=MessageNames.GAME_JOIN, data=self.game_id)
        await ws.send(om.json())

    async def on_message(self, msg: IncomingMessage, ws: WebSocket):
        try:
            if msg.name == MessageNames.GAME_STATUS:
                pass
            elif msg.name == MessageNames.LOG:
                self.logger.debug(msg)
            else:
                self.logger.debug(msg)
        except TypeError as e:
            self.logger.exception(e)


class Client(_BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_concurrent_games = int(kwargs.pop("max_concurrent_games", 0))
        self.output_queue: asyncio.Queue = asyncio.Queue()
        self.games: T.Dict[T.AnyStr, T.Tuple[GameClient, T.Awaitable]] = dict()
        self.finished_games: asyncio.Queue = asyncio.Queue()
        self._lck_games = asyncio.Lock()

    async def on_connection_made(self, ws: WebSocket):
        await super().on_connection_made(ws)
        self.tasks.extend([
            asyncio.create_task(self.process_output_queue(ws)),
            asyncio.create_task(self.collect_finished_games()),
            asyncio.create_task(
                self.send_command(ws, MessageNames.GAMES_LIST, 1)
            ),
            # asyncio.create_task(
            #     self.send_command(ws, MessageNames.ACCOUNT_INFO, 2)
            # ),
        ])

    async def on_message(self, msg: IncomingMessage, ws: WebSocket):
        try:
            if msg.name == MessageNames.GAMES_LIST:
                for game_data in msg.data:
                    g = Game.fromdata(game_data)
                    # PLAY GAMES
                    async with self._lck_games:
                        if await self.wants_to_play(g):
                            self.logger.info("WANT: %s, %s, %s",
                                             g.game_id, self, len(self.games))
                            await self.spawn_game_client(g)
                    # PLACE BETS
                    if await self.wants_to_bet(g):
                        pass
            elif msg.name == MessageNames.GAME_BET:
                self.logger.info(msg)
        except TypeError as e:
            self.logger.exception(e)

    async def wants_to_play(self, game: Game):
        self.logger.debug(game)
        if len(self.games) >= self.max_concurrent_games:
            self.logger.debug(
                "max_concurrent_games, (SKIP: %s) ",
                game.game_id)
            return False
        return str(game.game_id) not in self.games

    async def wants_to_bet(self, game: Game):
        # return str(game.game_id) not in self.games
        return False

    async def spawn_game_client(self, game: Game):
        async def _play_game(game_client, g):
            self.logger.info("Starting game client: %s", g.game_id)
            await game_client.start()
            self.logger.info("game client finished: %s", g.game_id)
            await self.finished_games.put(g.game_id)

        self.logger.debug(game.game_id)

        url = urljoin(self.url, game.url)
        game_client = GameClient(
            game.game_id,
            url,
            headers=self.headers,
            stop_ev=self.stop_ev,
        )
        self.games[str(game.game_id)] = (
            game_client,
            asyncio.create_task(_play_game(game_client, game))
        )

    async def collect_finished_games(self):
        while not self.stop_ev.is_set() and not self._is_finished:
            await self.try_collect_finished_game()

        while not self.finished_games.empty():
            await self.try_collect_finished_game()

    async def try_collect_finished_game(self):
        try:
            game_id = await asyncio.wait_for(self.finished_games.get(),
                                             timeout=0.1)

            gc, task = self.games.pop(str(game_id))
            await task
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            self.logger.exception(e)

    async def process_output_queue(self, ws):
        while not self.stop_ev.is_set() and not self._is_finished:
            try:
                msg = await asyncio.wait_for(
                    self.output_queue.get(),
                    timeout=0.1
                )
                await ws.send(msg)
                self.output_queue.task_done()
                self.logger.info(msg)
            except asyncio.TimeoutError:
                pass
            except (websockets.WebSocketException,
                    Exception) as e:
                self.logger.exception(e)
                break
