from dataclasses import dataclass, field
import datetime
import types
from typing import Optional

from .mixins import PayloadIniter
from . import utils


@dataclass(frozen=True, init=False)
class Player(PayloadIniter):
    """Represents a player.

    Attributes:
    created_at (datetime.datetime): When the player was first created
        on battlemetrics as a naive UTC datetime.
    first_time (Optional[bool]):
        Whether this is the first time the player is on the server.
    id (int): The player's id.
    name (str): The player's name.
    score (Optional[int]): The player's in-game score.
    payload (dict): A read-only view of the raw payload.
    playtime (Optional[float]): How long the player has been in the server
        for their current session in seconds.
    updated_at (datetime.datetime):
        When this player was last updated as a naive UTC datetime.

    """
    __init_attrs = (
        {'name': 'id', 'type': int},
        {'name': 'name', 'path': ('attributes', 'name')}
    )
    _init_meta = ({'name': 'first_time', 'path': 'firstTime'},
                  'score', {'name': 'playtime', 'path': 'time'})

    created_at: datetime.datetime = field(hash=False, repr=False)
    first_time: Optional[bool]    = field(hash=False, repr=False)
    id: int
    name: str                     = field(hash=False)
    score: Optional[int]          = field(hash=False, repr=False)
    payload: dict                 = field(hash=False, repr=False)
    playtime: Optional[float]     = field(hash=False, repr=False)
    updated_at: datetime.datetime = field(hash=False, repr=False)

    def __init__(self, payload):
        def flatten_meta():
            return {x['key']: x['value'] for x in payload['meta']['metadata']}

        super().__setattr__('payload', types.MappingProxyType(payload))

        self.__init_attrs__(payload, self.__init_attrs)
        self.__init_attrs__(flatten_meta(), self._init_meta, required=False)

        attrs = payload['attributes']
        super().__setattr__('created_at', utils.parse_datetime(attrs['createdAt']))
        super().__setattr__('updated_at', utils.parse_datetime(attrs['updatedAt']))
