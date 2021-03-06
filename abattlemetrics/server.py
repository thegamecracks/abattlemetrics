from dataclasses import dataclass, field
import datetime
import types
from typing import Optional, Tuple

from .mixins import PayloadIniter
from .player import Player
from . import utils

__all__ = ('Server',)


@dataclass(frozen=True, init=False)
class Server(PayloadIniter):
    """Represents a server returned by get_server_info().

    Attributes:
    address (Optional[str]): The server address, e.g. play.example.com
    country (str): The country code that the server is hosted in.
    created_at (datetime.datetime):
        When the server was created on battlemetrics as an aware datetime.
    details (dict): A dict with more specific details on the server's settings,
        such as difficulty, map, or game version.
    id (int): The server's ID.
    ip (str): The IPv4 address of the server.
    max_players (int): The maximum number of players the server allows.
    name (str): The server name.
    payload (dict): A read-only view of the raw payload.
    player_count (int): The number of players in the server.
    players (tuple): A list of Player objects. This may be empty if the query
        did not specify to include player data.
    port (int): The server's port.
    private (bool): Whether the server is private or not.
    query_port (int): The server's query port.
    rank (int): The server's rank on battlemetrics's leaderboards.
    status (str): The status of the server, i.e. "online" or "offline"
    updated_at (datetime.datetime):
        When the server was last updated on battlemetrics as an aware datetime.

    """
    __init_attrs = (
        {'name': 'created_at', 'type': utils.parse_datetime,
         'path': 'createdAt'},
        'address', 'country', 'details', {'name': 'id', 'type': int}, 'ip',
        {'name': 'max_players', 'path': 'maxPlayers'}, 'name',
        {'name': 'player_count', 'path': 'players'}, 'port',
        {'name': 'query_port', 'path': 'portQuery'}, 'private',
        'rank', 'status',
        {'name': 'updated_at', 'type': utils.parse_datetime,
         'path': 'updatedAt'}
    )

    address: Optional[str]        = field(hash=False, repr=False)
    country: str                  = field(hash=False, repr=False)
    created_at: datetime.datetime = field(hash=False, repr=False)
    details: dict                 = field(hash=False, repr=False)
    id: int
    ip: str                       = field(hash=False, repr=False)
    max_players: int              = field(hash=False, repr=False)
    name: str                     = field(hash=False)
    payload: dict                 = field(hash=False, repr=False)
    player_count: int             = field(hash=False, repr=False)
    players: Tuple[Player]        = field(hash=False, repr=False)
    port: int                     = field(hash=False, repr=False)
    private: bool                 = field(hash=False, repr=False)
    query_port: int               = field(hash=False, repr=False)
    rank: int                     = field(hash=False, repr=False)
    status: str                   = field(hash=False, repr=False)
    updated_at: datetime.datetime = field(hash=False, repr=False)

    def __init__(self, payload):
        super().__setattr__('payload', types.MappingProxyType(payload))

        data = payload.get('data')
        if data:
            attrs = data['attributes']
        else:
            attrs = payload['attributes']

        self.__init_attrs__(attrs, self.__init_attrs)

        included = payload.get('included')
        players = ()
        if included:
            players = tuple(
                Player(item) for item in included
                if item['type'] == 'player'
            )
        super().__setattr__('players', players)
