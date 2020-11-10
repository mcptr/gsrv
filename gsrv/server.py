from gsrv import handlers
from gsrv.router import Router
from gsrv.connection import Connection
from gsrv.errors import AuthError
from gsrv.api import accounts
from gsrv.dtypes import Auth

from gcore.constants import URL_PREFIX_MAIN, URL_PREFIX_GAMES

import websockets
import asyncio


class Server:
    def __init__(self, rt, host, port):
        self.logger = rt.get_logger(self.__class__.__name__)
        self.rt = rt
        self.host = host
        self.port = port
        self.is_ready = asyncio.Event()

        self.router = Router({
            URL_PREFIX_MAIN: handlers.MainHandler,
            "%s/<UUID:game_id>" % URL_PREFIX_GAMES: handlers.GameHandler,
        })

    async def start(self):
        srv_params = (self.handle_client, self.host, self.port)
        async with websockets.serve(*srv_params) as srv:
            assert srv.is_serving()
            self.is_ready.set()
            self.logger.info("Waiting for: %r", self.rt.stop_ev)
            await self.rt.stop_ev.wait()
            srv.close()
            await srv.wait_closed()

    async def handle_client(self, ws, path):
        try:
            cls, params = self.router.get(path)
            connection = Connection(ws=ws)
            if not cls:
                await connection.reject("No such resource: %s" % path)
                return
            elif cls.REQUIRES_AUTH:
                await self.authenticate(connection)

            handler = cls(self.rt)
            await handler.handle_session(connection, **(params or {}))
        except AuthError as e:
            self.logger.error("%s (account_id=%s)", e, connection.account_id)
            await connection.reject("Authentication failed")

    async def authenticate(self, connection):
        api_key = connection.request_headers.get("x-api-key", None)
        account = None
        if connection.account_id and api_key:
            auth = Auth(account_id=connection.account_id, api_key=api_key)
            account = await accounts.authenticate(self.rt, auth)

        if not account:
            raise AuthError()
