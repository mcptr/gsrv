# from gcli import dtypes
from gcore import cli, aio
from gcli.client import Client

import asyncio
import os


STOP_EVENT = asyncio.Event()


# FIXME: Move this away from here
HEADERS = {
    "x-account-id": os.environ.get(
        "ACCOUNT_ID", "c07a3b49-a795-4d3b-ad02-1527fd6029df"
    ),
    "x-api-key": os.environ.get(
        "API_KEY", "08537a0f-69b7-4f4c-9db7-11182d360b7f"
    )
}


def terminate(*args, **kwargs):
    global STOP_EVENT
    STOP_EVENT.set()


async def main(args):
    c = Client(
        args.url,
        max_concurrent_games=1,
        headers=HEADERS,
        stop_ev=STOP_EVENT,
    )
    await c.start()


if __name__ == "__main__":
    import argparse

    LOG_FORMAT = " ".join([
        "%(levelname)-8s %(name)-16s %(module)-24s %(message)s",
    ])

    parser = argparse.ArgumentParser(parents=[
        cli.create_generic_parser(),
    ])

    parser.add_argument("url", type=str, default="ws://localhost:9876")

    args = parser.parse_args()
    cli.setup_basic_logging(debug=args.debug)
    aio.run(main(args), terminate=terminate, **args.__dict__)
