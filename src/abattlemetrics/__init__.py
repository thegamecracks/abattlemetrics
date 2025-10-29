from .client import *
from .datapoint import *
from .errors import *
from .iterators import *
from .player import *
from .server import *
from .session import *


def _get_version() -> str:
    from importlib.metadata import version

    return version("ministatus")


__version__ = _get_version()
