from gcore.constants import URL_PREFIX_GAMES

import sys
import json
import logging
import uuid
import enum
import typing as T
from pydantic import BaseModel, Field
from datetime import datetime
from urllib.parse import ParseResult
from websockets import WebSocketServerProtocol


WebSocket = WebSocketServerProtocol


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.name
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, ParseResult):
            return obj._asdict()
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


class Base(BaseModel):
    type_id: T.Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_id = self.__class__.__name__

    @classmethod
    def load(cls, path):
        with open(path, "r") as fh:
            return cls(**json.load(fh))

    @classmethod
    def loads(cls, json_str, *, safe=False, auto_cast=False):
        """
        This is hacky-automation. Either current cls or auto cast
        to the type specified in type_id. This should have probably been
        a regular factory instead. Needs to work in gcli and gsrv
        without mutual dependencies between them.
        """
        try:
            o = json.loads(json_str)
            type_id = o.get("type_id", None)
            if auto_cast and (type_id and type_id != cls.__name__):
                return cls.fromdata(o)
            else:
                return cls(**o)
        except (TypeError, json.decoder.JSONDecodeError) as e:
            logging.error("%s: %s", cls.__name__, e)
            if not safe:
                raise
        return None

    def dump(self, path, **kwargs):
        with open(path, "w") as fh:
            fh.write(self.asjson(**kwargs))

    def dumps(self, *args, **kwargs):
        return json.dumps(self.dict(), cls=JSONEncoder, **kwargs)

    def astuple(self, fields):
        return tuple([getattr(self, f) for f in fields])

    @staticmethod
    def fromdata(data):
        """
        Factory for all the types defined in this module (inc. derivatives).
        Hopefully a useful hack.
        """
        try:
            cls = getattr(sys.modules[__loader__.name], data.get("type_id"))
            return cls(**data) if cls else None
        except AttributeError:
            return None


class MessageNames:
    # /
    GAMES_LIST = "games/list"
    ACCOUNT_INFO = "account/info"
    # /games
    GAME_JOIN = "game/join"
    GAME_STATUS = "game/status"
    GAME_BET = "game/bet"
    LOG = "log"


class Message(Base):
    name: T.Optional[str] = None
    data: T.Optional[T.Any] = None

    def __str__(self):
        return self.json()


class ServerMessage(Message):
    ctime_utc: datetime = Field(default_factory=datetime.utcnow)
    code: int = 0


class ErrorMessage(ServerMessage):
    code: int = 1


class LogMessage(ServerMessage):
    name: str = MessageNames.LOG


class Bet(Base):
    game_id: uuid.UUID


class GameStrategy_t(enum.Enum):
    TBS = enum.auto()
    RTS = enum.auto()


class GameSettings(Base):
    strategy: GameStrategy_t = GameStrategy_t.TBS
    min_players: int = 1
    max_players: int = 64
    cost_to_join: float = 0


class GameState(Base):
    players: T.List[str] = Field(default_factory=list)

    is_finished: bool = False
    is_cancelled: bool = False
    is_blind: bool = False
    round_idx: int = 0
    current_player_idx: int = 0

    winners: T.List = Field(default_factory=list)
    moves: T.List[T.Any] = Field(default_factory=list)

    start_utc: T.Optional[datetime] = None
    end_utc: T.Optional[datetime] = None
    sha256_sum: str = None


class Game(Base):
    game_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    settings: GameSettings = Field(default_factory=GameSettings)
    state: GameState = Field(default_factory=GameState)
    url: T.Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = "/".join([URL_PREFIX_GAMES, str(self.game_id)])

    def cancel(self):
        self.state.is_cancelled = True
        self.finish()

    def finish(self):
        self.state.is_finished = True

    def add_player(self, player_id):
        if(player_id not in self.state.players
           and len(self.state.players) < self.settings.max_players):
            self.state.players.append(player_id)
            return True
        return False

    def remove_player(self, player_id):
        if player_id in self.state.players:
            idx = self.state.players.index(player_id)
            self.state.players[idx] = None
            # self.broadcast_state()

    async def start(self):
        import asyncio
        await asyncio.sleep(4)


class GuessARandom(Game):
    pass
