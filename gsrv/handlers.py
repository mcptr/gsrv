from gsrv.connection import Connection
from gsrv.runtime import RT
from gsrv.dtypes import (
    MessageNames,
    IncomingMessage,
    OutgoingMessage,
    ErrorMessage,
)

import websockets
# import asyncio
import uuid

import abc


class Handler(abc.ABC):
    def __init__(self, rt: RT):
        self.logger = rt.get_logger(self.__class__.__name__)
        self.rt = rt
        self.tasks = []

    @abc.abstractmethod
    async def on_message(self,
                         msg: IncomingMessage,
                         connection: Connection) -> None:
        pass

    async def process_messages(self, connection: Connection) -> None:
        try:
            async for msg in connection.ws:
                msg = IncomingMessage.loads(msg)
                await self.on_message(msg, connection)
        except (websockets.WebSocketException) as e:
            self.logger.error(e)
        except Exception as e:
            self.logger.error(e)
            await connection.reject()

    async def handle_session(self, connection: Connection, **kwargs) -> None:
        await self.process_messages(connection)


class MainHandler(Handler):
    REQUIRES_AUTH = True

    async def on_message(self,
                         msg: IncomingMessage,
                         connection: Connection) -> None:
        if msg.name == MessageNames.ACCOUNT_INFO:
            msg = ErrorMessage(name=msg.name)
            await connection.send(msg.json())
        elif msg.name == MessageNames.GAMES_LIST:
            games = [gr.game for gr in self.rt.games.values()]
            msg = OutgoingMessage(
                name=msg.name,
                data=games,
            )
            await connection.send(msg.json())
        elif msg.name == MessageNames.GAME_BET:
            msg = ErrorMessage(name=msg.name)
            await connection.send(msg.json())


class GameHandler(Handler):
    REQUIRES_AUTH = True

    async def handle_session(self,
                             connection: Connection,
                             *,
                             game_id: uuid.UUID = None) -> None:
        gr = self.rt.games.get(str(game_id))
        if not gr:
            await connection.reject("No such game")
        else:
            await gr.add_connection(connection)
            # await self.process_messages(connection)

    async def on_message(self,
                         msg: IncomingMessage,
                         connection: Connection) -> None:
        ...
