from dataclasses import dataclass, field
import datetime
from typing import List, Optional

from .mixins import DatetimeParser, PayloadIniter


@dataclass(init=False, frozen=True)
class Player(DatetimeParser, PayloadIniter):
    """Represents a player.

    Attributes:
    created_at (datetime.datetime): When the player was first created
        on battlemetrics as a naive UTC datetime.
    first_time (bool):
        Whether this is the first time the player is on the server.
    id (int): The player's id.
    name (str): The player's name.
    score (int): The player's ingame score.
    playtime (float): How long the player has been in the server
        for their current session in seconds.
    updated_at (datetime.datetime):
        When this player was last updated as a naive UTC datetime.

    """
    _init_attrs = (
        {'name': 'id', 'type': int},
        {'name': 'name', 'path': ('attributes', 'name')}
    )
    _init_meta = ({'name': 'first_time', 'path': 'firstTime'},
                  'score', {'name': 'playtime', 'path': 'time'})

    created_at: datetime.datetime = field(hash=False, repr=False)
    first_time: bool              = field(hash=False, repr=False)
    id: int
    name: str                     = field(hash=False)
    score: int                    = field(hash=False, repr=False)
    playtime: float               = field(hash=False, repr=False)
    updated_at: datetime.datetime = field(hash=False, repr=False)

    def __init__(self, payload):
        def flatten_meta():
            return {x['key']: x['value'] for x in payload['meta']['metadata']}

        self.__init_attrs__(payload, self._init_attrs)
        self.__init_attrs__(flatten_meta(), self._init_meta)

        attrs = payload['attributes']
        super().__setattr__('created_at', self._parse_datetime(attrs['createdAt']))
        super().__setattr__('updated_at', self._parse_datetime(attrs['updatedAt']))

