import os


DEBUG = int(os.environ.get("DEBUG", 0))
PG_URL = os.environ.get("PG_URL", "postgresql://localhost/gsrv")
PG_POOL_MINSIZE = 4
PG_POOL_MAXSIZE = 32

MAX_CONCURRENT_GAMES = 1
GAME_PENDING_TIMEOUT = 6.0
