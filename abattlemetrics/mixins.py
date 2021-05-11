import datetime


class DatetimeParsable:
    """A mixin that provides the datetime format used by battlemetrics along
    with a helper method."""
    _datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    @classmethod
    def _parse_datetime(cls, date_string: str) -> datetime.datetime:
        return datetime.datetime.strptime(date_string, cls._datetime_format)
