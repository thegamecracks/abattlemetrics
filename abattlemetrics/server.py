from dataclasses import dataclass, field
import datetime
from typing import List, Optional

from .mixins import DatetimeParser, PayloadIniter
from .player import Player


@dataclass(init=False, frozen=True)
class Server(DatetimeParser, PayloadIniter):
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
    name (str): The server name.
    player_count (int): The number of players in the server.
    players (list): A list of Player objects. This may be empty if the query
        did not specify to include player data.
    port (int): The server's port.
    private (bool): Whether the server is private or not.
    query_port (int): The server's query port.
    rank (int): The server's rank on battlemetrics's leaderboards.
    status (str): The status of the server, i.e. "online" or "offline"
    updated_at (datetime.datetime):
        When the server was last updated on battlemetrics as a naive UTC datetime.

    """
    _init_attrs = (
        'address', 'country', 'details', {'name': 'id', 'type': int}, 'ip',
        {'name': 'max_players', 'path': 'maxPlayers'}, 'name',
        {'name': 'player_count', 'path': 'players'}, 'port',
        {'name': 'query_port', 'path': 'portQuery'}, 'private',
        'rank', 'status'
    )

    address: Optional[str] = field(repr=False)
    country: str = field(repr=False)
    created_at: datetime.datetime = field(repr=False)
    details: dict = field(repr=False)
    id: int
    ip: str = field(repr=False)
    max_players: int = field(repr=False)
    name: str
    player_count: int = field(repr=False)
    players: List[Player] = field(repr=False)
    port: int = field(repr=False)
    private: bool = field(repr=False)
    query_port: int = field(repr=False)
    rank: int = field(repr=False)
    status: str = field(repr=False)
    updated_at: datetime.datetime = field(repr=False)

    def __init__(self, payload):
        attrs = payload['data']['attributes']
        self.__init_attrs__(attrs, self._init_attrs)
        super().__setattr__('created_at', self._parse_datetime(attrs['createdAt']))
        super().__setattr__('updated_at', self._parse_datetime(attrs['updatedAt']))

        players = []
        for item in payload['included']:
            if item['type'] == 'player':
                players.append(Player(item))
        super().__setattr__('players', players)
