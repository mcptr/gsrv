import argparse
import logging
import os
# from termcolor import colored


LOG_FORMAT = " ".join([
    "%(levelname)-8s %(asctime)s | %(name)-24s",
    "%(funcName)-32s | %(message)s",
])


# class C:
#     ENABLED = False
#     RED = (lambda s: colored(s, "red") if C.ENABLED else s)
#     GREEN = (lambda s: colored(s, "green") if C.ENABLED else s)
#     BLUE = (lambda s: colored(s, "blue") if C.ENABLED else s)
#     YELLOW = (lambda s: colored(s, "yellow") if C.ENABLED else s)
#     MAGENTA = (lambda s: colored(s, "magenta") if C.ENABLED else s)
#     CYAN = (lambda s: colored(s, "cyan") if C.ENABLED else s)
#     GREY = (lambda s: colored(s, "grey") if C.ENABLED else s)
#     WHITE = (lambda s: colored(s, "white") if C.ENABLED else s)
#     R = RED
#     G = GREEN
#     B = BLUE
#     Y = YELLOW
#     M = MAGENTA
#     C = CYAN
#     W = WHITE
#     HEADER = (lambda s: colored(s, "cyan", attrs=["reverse", "bold"])
#               if C.ENABLED else s)
#     HOST = (lambda s: colored(s, "cyan", attrs=["reverse"])
#             if C.ENABLED else s)
#     INFO = (lambda s: colored(s, "blue")
#             if C.ENABLED else s)
#     INFO_R = (lambda s: colored(s, "blue", attrs=["reverse"])
#               if C.ENABLED else s)


def create_generic_parser(*args, **kwargs):
    parser = argparse.ArgumentParser(add_help=kwargs.pop("add_help", False))
    group = parser.add_argument_group("Generic")
    group.add_argument("-D", "--debug", action="store_true")
    group.add_argument("-A", "--aio-debug", action="store_true")
    group.add_argument("-E", "--aio-no-exception-handler", action="store_true")
    group.add_argument("-v", "--verbose", action="store_true")
    return parser


def setup_basic_logging(**kwargs):
    fmt = kwargs.pop("fmt", LOG_FORMAT)
    is_debug = int(os.environ.get("DEBUG", kwargs.get("debug", 0)))
    logging.basicConfig(
        level=(logging.DEBUG if is_debug else logging.INFO),
        format=fmt,
    )


def get_logger(name, **kwargs):
    return logging.getLogger(name)
