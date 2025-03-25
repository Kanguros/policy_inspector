import logging
from typing import Callable

from click import option
from pydantic import BaseModel


# It's just make use of pydantic because it's available ;)
class Example(BaseModel):
    name: str
    args: list
    cmd: Callable


def verbose_option() -> Callable:
    """Wrapper around Click ``option``. Sets logger and its handlers to the ``DEBUG`` level."""

    def callback(ctx, param, value) -> None:
        if not value:
            return
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    kwargs = {
        "is_flag": True,
        "callback": callback,
        "expose_value": False,
        "is_eager": True,
        "help": "Set log messages to DEBUG",
    }
    return option("-v", "--verbose", **kwargs)
