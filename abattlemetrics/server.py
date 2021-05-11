import dataclasses
import datetime
from typing import Optional

from .mixins import DatetimeParsable


@dataclasses.dataclass(init=False, frozen=True)
class Server(DatetimeParsable):
    """Represents a server returned by get_server_info().

    Attributes:
    address (Optional[str]): The server address, e.g. play.example.com
    country (str): The country code that the server is hosted in.
    created_at (datetime.datetime):
        When the server was created on battlemetrics as a naive UTC datetime.
    details (dict): A dict with more specific details on the server's settings,
        such as difficulty, map, or game version.
    id (int): The server's ID.
    ip (str): The IPv4 address of the server.
    max_players (int): The maximum number of players the server allows.
    port (int): The server's port.
    private (bool): Whether the server is private or not.
    query_port (int): The server's query port.
    rank (int): The server's rank on battlemetrics's leaderboards.
    status (str): The status of the server, i.e. "online" or "offline"
    updated_at (datetime.datetime):
        When the server was last updated on battlemetrics as a naive UTC datetime.

    """
    _init_attrs = (
        'address', 'country', 'details', 'id', 'ip',
        ('max_players', 'maxPlayers'), 'name', 'players', 'port',
        ('query_port', 'portQuery'), 'private', 'rank', 'status'
    )

    address: Optional[str]
    country: str
    created_at: datetime.datetime
    details: dict
    id: int
    ip: str
    max_players: int
    name: str
    players: int
    port: int
    private: bool
    query_port: int
    rank: int
    status: str
    updated_at: datetime.datetime

    def __init__(self, payload):
        attrs = payload['data']['attributes']
        for x in self._init_attrs:
            if isinstance(x, tuple):
                super().__setattr__(x[0], attrs[x[1]])
            else:
                super().__setattr__(x, attrs[x])
        super().__setattr__('created_at', self._parse_datetime(attrs['createdAt']))
        super().__setattr__('updated_at', self._parse_datetime(attrs['updatedAt']))
