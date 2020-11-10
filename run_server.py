from gsrv import settings, pg
from gsrv.runtime import RT
from gsrv.server import Server
from gsrv.game_runner import GameRunner

import typing as T

import asyncio
import os
from gcli.client import Client


# FIXME: Move this away from here
CLIENT_ACCOUNT_ID = os.environ.get(
    "ACCOUNT_ID", "c07a3b49-a795-4d3b-ad02-1527fd6029df")

CLIENT_API_KEY = os.environ.get(
    "API_KEY", "08537a0f-69b7-4f4c-9db7-11182d360b7f")


G_RUNTIMES = {}
BOTS = []


def create_bots(stop_ev, uri="ws://127.0.0.1:8000", n_bots=1):
    global BOTS
    bots = [
        Client(
            uri,
            stop_ev=stop_ev,
            max_concurrent_games=1,
            headers={
                "x-account-id": CLIENT_ACCOUNT_ID,
                "x-api-key": CLIENT_API_KEY,
            }
        )
        for i in range(n_bots)
    ]

    BOTS.extend(bots)
    return bots


def terminate(*args, **kwargs):
    global G_RUNTIMES, BOTS
    [rt.stop() for rt in G_RUNTIMES.values()]
    [c.stop_ev.set() for c in BOTS]


async def initialize(rt: RT,
                     *,
                     pg_url: T.Optional[str] = None,
                     pg_pool_minsize: T.Optional[int] = 1,
                     pg_pool_maxsize: T.Optional[int] = 32,
                     **kwargs):
    rt.pgpool = await pg.create_pg_pool(
        pg_url,
        minsize=pg_pool_minsize,
        maxsize=pg_pool_maxsize,
        **kwargs
    )


async def shutdown(rt, **kwargs):
    await rt.pgpool.close()


async def run_bots(args, srv):
    global BOTS

    await asyncio.wait_for(srv.is_ready.wait(), timeout=3)

    create_bots(
        srv.rt.stop_ev,
        "ws://{host}:{port}".format(**args.__dict__),
        n_bots=args.bots)

    await asyncio.gather(
        *[asyncio.create_task(b.start()) for b in BOTS])


async def main(args):
    global G_RUNTIMES  # global, as we use them in signal handlers

    rt = RT()
    G_RUNTIMES[rt.rt_id] = rt

    await initialize(rt, **args.__dict__)

    srv = Server(rt, args.host, args.port)

    tasks = [
        asyncio.create_task(GameRunner(rt).start()),
        asyncio.create_task(srv.start()),
        asyncio.create_task(run_bots(args, srv)),
    ]

    await asyncio.gather(*tasks)
    await shutdown(rt, **args.__dict__)


if __name__ == "__main__":
    import argparse
    from gcore import aio
    from gsrv import cli

    parser = argparse.ArgumentParser(parents=[
        cli.create_generic_parser(),
        cli.create_pg_parser(pg_url=settings.PG_URL),
        # cli.create_redis_parser(),
    ])

    parser.add_argument("-b", "--bots", type=int, default=0)
    parser.add_argument("-H", "--host", type=str, default="127.0.0.1")
    parser.add_argument("-p", "--port", type=int, default=8000)

    args = parser.parse_args()
    cli.setup_basic_logging(debug=args.debug)

    aio.run(main(args), terminate=terminate, **args.__dict__)
