from typing import Tuple, Union


class PayloadIniter:
    """Provides an __init_attrs__ method for extracting attributes
    from a payload. Use __init_attrs to specify the attributes.

    """

    def __init_attrs__(
        self,
        attrs,
        mapping: Tuple[Union[str, dict], ...],
        *,
        required=True,
    ):
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
            {'name': 'score', 'default': 0}
                Reads the "score" key and if it exists, assigns it
                to `score`, otherwise the `default` value is used.
                Does not convert to `type`.
            {'name': 'identifier', 'default_factory': dict}
                Reads the "identifier" key and if it exists, assigns it
                to `identifier`, otherwise `default_factory` is called
                for a value. Does not convert to `type`.

        Args:
            attrs (dict): A dictionary of attributes to extract values from.
                This is usually a payload.
            mapping (Tuple[Dict[str, object]]):
                The mapping to follow when extracting attributes from attrs.
            required (bool): If True, all specified attributes that do not
                have a default or default_factory must exist.
                Otherwise, some keys can be missing from attrs, in
                which case their corresponding attribute is set to None.

        Raises:
            KeyError: An attribute specified in mapping was missing from attrs.
        """

        def lookup(p):
            v = attrs
            for k in p:
                try:
                    v = v[k]
                except (KeyError, TypeError):
                    if required:
                        raise KeyError(f"attrs is missing {k!r} from {v!r}")
                    return
            return v

        missing = object()

        for x in mapping:
            if isinstance(x, str):
                super().__setattr__(x, lookup((x,)))
            else:
                name, path = x["name"], x.get("path")
                if path is None:
                    path = name
                if isinstance(path, str):
                    path = (path,)

                try:
                    val = lookup(path)
                except KeyError as e:
                    val = x.get("default", missing)
                    if val is missing:
                        val = x.get("default_factory", missing)
                        if val is missing:
                            raise e
                        val = val()

                conv = x.get("type")
                if conv is not None:
                    val = conv(val)

                super().__setattr__(x["name"], val)
