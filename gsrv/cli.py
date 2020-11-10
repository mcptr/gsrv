import argparse

from gcore.cli import (  # noqa
    create_generic_parser,
    setup_basic_logging,
    get_logger
)


def create_worker_parser(*args, **kwargs):
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_argument_group("Worker")
    group.add_argument("-C", "--concurrency", type=int, default=1)
    return parser


def create_pg_parser(*args, **kwargs):
    default_url = kwargs.pop("pg_url", "postgresql://localhost")
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_argument_group("Postgresql")
    group.add_argument("--pg-url", default=default_url)
    group.add_argument("--pg-timeout", type=int, default=3)
    group.add_argument("--pg-pool-minsize", type=int, default=2)
    group.add_argument("--pg-pool-maxize", type=int, default=10)
    return parser


def create_redis_parser(*args, **kwargs):
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_argument_group("Redis")
    group.add_argument("--redis-url", default="redis://localhost")
    group.add_argument("--redis-pool-minsize", type=int, default=1)
    group.add_argument("--redis-pool-maxsize", type=int, default=32)
    return parser
