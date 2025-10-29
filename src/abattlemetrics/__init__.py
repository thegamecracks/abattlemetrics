from .client import BattleMetricsClient as BattleMetricsClient
from .datapoint import DataPoint as DataPoint, Resolution as Resolution
from .errors import (
    BattleMetricsException as BattleMetricsException,
    HTTPException as HTTPException,
)
from .iterators import (
    AsyncIterator as AsyncIterator,
    AsyncPlayerListIterator as AsyncPlayerListIterator,
    AsyncSessionIterator as AsyncSessionIterator,
)
from .player import (
    IdentifierType as IdentifierType,
    Identifier as Identifier,
    Player as Player,
)
from .server import Server as Server
from .session import Session as Session


def _get_version() -> str:
    from importlib.metadata import version

    return version("ministatus")


__version__ = _get_version()
