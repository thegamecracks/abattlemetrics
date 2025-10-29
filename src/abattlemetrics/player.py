from dataclasses import dataclass, field
import datetime
import enum
import types
from typing import Optional, Tuple

from .mixins import PayloadIniter
from . import utils

__all__ = ("IdentifierType", "Identifier", "Player")


class IdentifierType(enum.Enum):
    """A player identifier type."""

    # fmt: off
    BE_GUID                  = "BEGUID"
    BE_LEGACY_GUID           = "legacyBEGUID"
    CONAN_CHAR_NAME          = "conanCharName"
    EGS_ID                   = "egsID"
    FUNCOM_ID                = "funcomID"
    IP                       = "ip"
    MC_UUID                  = "mcUUID"
    NAME                     = "name"
    PLAY_FAB_ID              = "playFabID"
    STEAM_FAMILY_SHARE_OWNER = "steamFamilyShareOwner"
    STEAM_ID                 = "steamID"
    SURVIVOR_NAME            = "survivorName"
    # fmt: on

    def __repr__(self):
        return "<{0.__class__.__name__}.{0.name}>".format(self)


@dataclass(frozen=True, init=False)
class Identifier(PayloadIniter):
    """A player identifier.

    Attributes:
    id (int): The identifier ID.
        Note that this is not the actual player identifier.
    last_seen (datetime.datetime):
        The time this identifier was last seen as an aware datetime.
    metadata (dict): A read-only view of the payload metadata.
        This is supplied for certain identifiers, e.g. IP.
    name (Optional[str]): The player identifier.
        This may be None depending on the type, e.g. IP.
    payload (dict): A read-only view of the raw payload.
    player_id (int): The player ID this identifier is associated to.
    private (bool): Indicates if this should be considered private.
    type (IdentifierType): The type of identifier this is.

    """

    __init_attrs = (
        {"name": "id", "type": int},
        {
            "name": "last_seen",
            "type": utils.parse_datetime,
            "path": ("attributes", "lastSeen"),
        },
        {"name": "name", "path": ("attributes", "identifier"), "default": None},
        {
            "name": "player_id",
            "type": int,
            "path": ("relationships", "player", "data", "id"),
        },
        {"name": "private", "path": ("attributes", "private")},
        {"name": "type", "path": ("attributes", "type"), "type": IdentifierType},
    )

    id: int
    last_seen: datetime.datetime = field(hash=False, repr=False)
    metadata: dict = field(hash=False, repr=False)
    name: str = field(hash=False)
    payload: dict = field(hash=False, repr=False)
    player_id: int = field(hash=False, repr=False)
    private: bool = field(hash=False, repr=False)
    type: IdentifierType = field(hash=False, repr=False)

    def __init__(self, payload):
        super().__setattr__("payload", types.MappingProxyType(payload))

        self.__init_attrs__(payload, self.__init_attrs)

        metadata = payload["attributes"]["metadata"] or {}
        super().__setattr__("metadata", types.MappingProxyType(metadata))


@dataclass(frozen=True, init=False)
class Player(PayloadIniter):
    """Represents a player.

    Attributes:
    created_at (datetime.datetime): When the player was first created
        on battlemetrics as an aware datetime.
    first_time (Optional[bool]):
        Whether this is the first time the player is on the server.
    id (int): The player's id.
    identifiers (Tuple[Identifier, ...]):
        A tuple of Identifiers for this Player. Currently, this attribute
        is only provided by the `BattleMetricsClient.list_players()` endpoint.
    name (str): The player's name.
    score (Optional[int]): The player's in-game score.
    payload (dict): A read-only view of the raw payload.
    playtime (Optional[float]): How long the player has been in the server
        for their current session in seconds.
    positive_match (bool):
        When retrieved from a search with unique identifiers,
        this will be True if one of those identifiers exactly
        matches this player.
    private (bool): Indicates if the profile is private.
        Private profiles are excluded from search and player lists.
    updated_at (datetime.datetime):
        When this player was last updated as an aware datetime.

    """

    __init_attrs = (
        {
            "name": "created_at",
            "type": utils.parse_datetime,
            "path": ("attributes", "createdAt"),
        },
        {"name": "id", "type": int},
        {"name": "name", "path": ("attributes", "name")},
        {"name": "private", "path": ("attributes", "private")},
        {"name": "positive_match", "path": ("attributes", "positiveMatch")},
        {
            "name": "updated_at",
            "type": utils.parse_datetime,
            "path": ("attributes", "updatedAt"),
        },
    )
    _init_meta = (
        {"name": "first_time", "path": "firstTime"},
        "score",
        {"name": "playtime", "path": "time"},
    )

    # fmt: off
    created_at: datetime.datetime       = field(hash=False, repr=False)
    first_time: Optional[bool]          = field(hash=False, repr=False)
    id: int
    identifiers: Tuple[Identifier, ...] = field(hash=False, repr=False)
    name: str                           = field(hash=False)
    score: Optional[int]                = field(hash=False, repr=False)
    payload: dict                       = field(hash=False, repr=False)
    playtime: Optional[float]           = field(hash=False, repr=False)
    positive_match: bool                = field(hash=False, repr=False)
    private: bool                       = field(hash=False, repr=False)
    updated_at: datetime.datetime       = field(hash=False, repr=False)
    # fmt: bn

    def __init__(self, payload, identifiers=None):
        def flatten_meta(metadata):
            return {x["key"]: x["value"] for x in metadata}

        super().__setattr__("payload", types.MappingProxyType(payload))

        self.__init_attrs__(payload, self.__init_attrs)
        metadata = flatten_meta(payload.get("meta", {}).get("metadata", {}))
        self.__init_attrs__(metadata, self._init_meta, required=False)

        if identifiers:
            identifiers = tuple(Identifier(p) for p in identifiers)
        else:
            identifiers = ()
        super().__setattr__("identifiers", identifiers)
