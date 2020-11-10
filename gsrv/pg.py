from gsrv.dtypes import JSONEncoder
import asyncpg
import json
import logging
import contextlib
import psycopg2
import os


class PGError(Exception):
    pass


class AsyncPGConnection(asyncpg.Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    async def setup(cls, conn, *args, **kwargs):
        await conn.set_type_codec(
            "jsonb", schema="pg_catalog",
            encoder=(lambda v: (
                b"\x01" + json.dumps(
                    v,
                    default=JSONEncoder).encode("utf-8"))),
            decoder=(lambda v: json.loads(v[1:].decode("utf-8"))),
            format="binary"
        )
        await conn.set_type_codec(
            "numeric", encoder=str, decoder=float,
            schema="pg_catalog", format="text"
        )
        await conn.set_type_codec(
            "uuid", encoder=str.upper, decoder=str.upper,
            schema="pg_catalog", format="text"
        )
        # await conn.set_builtin_type_codec(
        #     "hstore", codec_name="pg_contrib.hstore")


@contextlib.asynccontextmanager
async def transaction(pool):
    async with pool.acquire() as pgconn:
        tx = pgconn.transaction()
        logging.debug("BEGIN")
        await tx.start()
        try:
            yield pgconn
        except Exception as e:
            logging.error(e)
            logging.debug("ROLLBACK")
            await tx.rollback()
            raise
        else:
            logging.debug("COMMIT")
            await tx.commit()


async def create_pg_pool(url=None, **kwargs):
    logging.debug("Initializing PG pool")
    pgpool = await asyncpg.create_pool(
        url,
        min_size=kwargs.pop("minsize", 1),
        max_size=kwargs.pop("maxsize", 10),
        timeout=kwargs.pop("timeout", 3),
        connection_class=AsyncPGConnection,
        init=AsyncPGConnection.setup,
    )
    return pgpool


def initdb_sync(url):
    """Needed for test class setup """
    sql_files = []
    sql_dir = os.path.join(os.path.dirname(__file__), "sql")
    with open(os.path.join(sql_dir, "loader.sql"), "r") as fh:
        lines = [
            line for line in fh.readlines()
            if line.startswith("\\i")
        ]
        sql_files.extend([line.split()[1] for line in lines])

    conn = psycopg2.connect(url)
    with conn.cursor() as cur:
        cur.execute("BEGIN")
        for f in sql_files:
            fpath = os.path.join(sql_dir, f)
            with open(fpath, "r") as sqlf:
                content = sqlf.read()
                if content:
                    cur.execute(content)
        cur.execute("COMMIT")
