from gcore.dtypes import (  # noqa
    Base,
    Field,
    JSONEncoder,
    WebSocket,

    Message,
    ServerMessage,
    ErrorMessage,
    LogMessage,

    MessageNames,

    Game,
    GuessARandom,

)
import uuid
import typing as T  # noqa


IncomingMessage = Message
OutgoingMessage = ServerMessage


class Account(Base):
    account_id: uuid.UUID


class Auth(Account):
    api_key: T.Optional[str] = None
