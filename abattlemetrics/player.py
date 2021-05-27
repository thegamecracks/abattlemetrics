from dataclasses import dataclass, field
import datetime
import enum
import types
from typing import Optional

from .mixins import PayloadIniter
from . import utils


class IdentifierType(enum.Enum):
    """A player identifier type.

    Types:
        BE[_LEGACY]_GUID: BattlEye GUID

    """
    BE_GUID                  = 'BEGUID'
    BE_LEGACY_GUID           = 'legacyBEGUID'
    CONAN_CHAR_NAME          = 'conanCharName'
    EGS_ID                   = 'egsID'
    FUNCOM_ID                = 'funcomID'
    IP                       = 'ip'
    MC_UUID                  = 'mcUUID'
    NAME                     = 'name'
    PLAY_FAB_ID              = 'playFabID'
    STEAM_FAMILY_SHARE_OWNER = 'steamFamilyShareOwner'
    STEAM_ID                 = 'steamID'
    SURVIVOR_NAME            = 'survivorName'

    def __repr__(self):
        return '<{0.__class__.__name__}.{0.name}>'.format(self)


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
        def flatten_meta(metadata):
            return {x['key']: x['value'] for x in metadata}

        super().__setattr__('payload', types.MappingProxyType(payload))

        self.__init_attrs__(payload, self.__init_attrs)
        metadata = flatten_meta(payload.get('meta', {}).get('metadata', {}))
        self.__init_attrs__(metadata, self._init_meta, required=False)

        attrs = payload['attributes']
        super().__setattr__('created_at', utils.parse_datetime(attrs['createdAt']))
        super().__setattr__('updated_at', utils.parse_datetime(attrs['updatedAt']))
