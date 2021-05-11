import datetime
from typing import Tuple, Union


class DatetimeParser:
    """A mixin that provides the datetime format used by battlemetrics along
    with a helper method."""
    _datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    @classmethod
    def _parse_datetime(cls, date_string: str) -> datetime.datetime:
        return datetime.datetime.strptime(date_string, cls._datetime_format)


class PayloadIniter:
    """Provides an __init_attrs__ method for extracting attributes
    from a payload. Use _init_attrs to specify the attributes.

    """

    def __init_attrs__(
            self, attrs, mapping: Tuple[Union[str, dict], ...], *,
            required=True):
        """Extract attributes into instance variables according to mapping.

        Each attr specified in mapping can be either a string, or a dictionary.
        A single string specifies both the instance attribute's name
        and the key in the attrs dict. A dictionary specifies the attribute's
        name as `name`, an optional key or sequence of keys for navigating
        the dictionary as `path`, and an optional `type` for converting
        the value.
        Examples:
            'address'
                Reads the "address" key and assigns it to `address`
            {'name': 'address'}
                Equivalent to above
            {'name': 'max_players', 'path': 'maxPlayers'}
                Reads the "maxPlayers" key and assigns it to `max_players`
            {'name': 'steam_id', 'path': ('details', 'serverSteamId'),
             'type': int}
                Reads the "serverSteamId" key inside "details", converts it
                to an integer, and assigns it to `steam_id`

        Args:
            attrs (dict): A dictionary of attributes to extract values from.
                This is usually a payload.
            mapping:
                The mapping to follow when extracting attributes from attrs.
            required (bool): If True, all specified attributes must exist.
                Otherwise, some keys can be missing from attrs, in
                which case their corresponding attribute is set to None.

        Raises:
            KeyError: An attribute specified in mapping was missing from attrs.
        """
        def lookup(p):
            v = attrs
            for x in p:
                try:
                    v = v[x]
                except (KeyError, TypeError) as e:
                    if required:
                        raise KeyError(f'attrs is missing {x!r} from {v!r}') from e
                    return
            return v

        for x in mapping:
            if isinstance(x, str):
                super().__setattr__(x, lookup((x,)))
            else:
                name, path = x['name'], x.get('path')
                if path is None:
                    path = name
                if isinstance(path, str):
                    path = (path,)
                val = lookup(path)

                conv = x.get('type')
                if conv is not None:
                    val = conv(val)

                super().__setattr__(x['name'], val)
