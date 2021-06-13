from dataclasses import dataclass, field
import datetime
import functools
import types
import pprint
from typing import Optional

from .mixins import PayloadIniter
from .server import Server
from . import utils


@dataclass(frozen=True, init=False)
class Session(PayloadIniter):
    """Represents a player session.

    Attributes:
    first_time (bool):
        Whether this is the first time the player is on the server.
    id (str): The session identifier.
    player_id (int): The player's ID.
    player_name (str): The player's name.
    payload (dict): A read-only view of the raw payload.
    playtime (float): How long this session has lasted in seconds.
        If `start` or `stop` is None, then this will be 0.
    server (Optional[Server]): The server this session took place in.
        This may be None if the server data was not included.
    server_id (int): The ID of the server this session took place in.
    start (Optional[datetime.datetime]):
        The start of the session as a naive UTC datetime.
        Battlemetrics may occasionally not provide this date.
    stop (Optional[datetime.datetime]):
        The end of the session as a naive UTC datetime.
        Battlemetrics may occasionally not provide this date.

    """
    __init_attrs = (
        {'name': 'first_time', 'path': ('attributes', 'firstTime')},
        'id',
        {'name': 'player_id', 'type': int,
         'path': ('relationships', 'player', 'data', 'id')},
        {'name': 'player_name', 'path': ('attributes', 'name')},
        {'name': 'server_id', 'type': int,
         'path': ('relationships', 'server', 'data', 'id')},
    )

    first_time: bool                   = field(hash=False, repr=False)
    id: str
    payload: dict                      = field(hash=False, repr=False)
    player_id: int                     = field(hash=False)
    player_name: str                   = field(hash=False, repr=False)
    server: Optional[Server]           = field(hash=False, repr=False)
    server_id: int                     = field(hash=False)
    start: Optional[datetime.datetime] = field(hash=False, repr=False)
    stop: Optional[datetime.datetime]  = field(hash=False, repr=False)

    def __init__(self, payload):
        super().__setattr__('payload', types.MappingProxyType(payload))
        # NOTE: server is manually assigned by AsyncSessionIterator

        self.__init_attrs__(payload, self.__init_attrs)

        attrs = payload['attributes']
        start, stop = attrs['start'], attrs['stop']
        start = utils.parse_datetime(start) if start else None
        stop = utils.parse_datetime(stop) if stop else None
        super().__setattr__('start', start)
        super().__setattr__('stop', stop)

    @functools.cached_property
    def playtime(self) -> float:
        if self.start is None or self.stop is None:
            return 0
        return (self.stop - self.start).total_seconds()
