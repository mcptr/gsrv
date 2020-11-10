from gsrv.dtypes import (
    Base,
    WebSocket,
)
import typing as T
import asyncio


class Connection(Base):
    ws: WebSocket
    remote_address: T.Optional[tuple] = None
    request_headers: T.Optional[dict] = None
    account_id: T.Optional[str] = None
    username: T.Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remote_address = ":".join(
            [str(x) for x in self.ws.remote_address]
        )
        self.request_headers = self.ws.request_headers
        self.account_id = self.request_headers.get("x-account-id")
        assert self.account_id, "No auth headers"
        self.username = "user-%s" % self.account_id.split("-")[-1]

    def __str__(self):
        return "Connection(%s)" % self.remote_address

    async def close(self, code: int = 1000, reason: str = ""):
        await self.ws.close(code, reason=str(reason))
        del self.ws
        self.ws = None

    async def reject(self, reason: str = "REJECTED"):
        return await self.close(1008, reason=str(reason))

    async def send(self, msg: T.Any):
        return await self.ws.send(str(msg))

    async def read(self, timeout_sec=5):
        return await asyncio.wait_for(self.ws.recv(), timeout=timeout_sec)
