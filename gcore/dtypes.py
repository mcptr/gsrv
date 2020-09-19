import json
import logging
import uuid
import typing as T
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from urllib.parse import ParseResult


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, ParseResult):
            return obj._asdict()
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


class Base(BaseModel):
    @classmethod
    def load(cls, path):
        with open(path, "r") as fh:
            return cls(**json.load(fh))

    @classmethod
    def loads(cls, json_str):
        try:
            return cls(**json.loads(json_str))
        except (TypeError, json.decoder.JSONDecodeError) as e:
            logging.error("%s: %s", cls.__name__, e)
        return None

    def dump(self, path, **kwargs):
        with open(path, "w") as fh:
            fh.write(self.asjson(**kwargs))

    def dumps(self, *args, **kwargs):
        return json.dumps(self.dict(), cls=JSONEncoder, **kwargs)

    def astuple(self, fields):
        return tuple([getattr(self, f) for f in fields])


class Auth(Base):
    account_id: uuid.UUID
    api_key: T.Optional[str] = None


class Message(Base):
    text: str
    data: T.Optional[T.Any] = None
    ctime_utc: datetime = Field(default_factory=datetime.utcnow)
    error_code: T.Optional[int] = 0
