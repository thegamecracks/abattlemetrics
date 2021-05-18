import datetime

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def isoify_datetime(dt: datetime.datetime) -> str:
    """Turn a datetime into a ISO formatted string in UTC suitable
    for parameters."""
    if dt.tzinfo:
        dt = dt.astimezone(datetime.timezone.utc)
    return dt.replace(microsecond=0, tzinfo=None).isoformat() + 'Z'


def parse_datetime(date_string: str) -> datetime.datetime:
    """Parse a datetime given by battlemetrics."""
    return datetime.datetime.strptime(date_string, DATETIME_FORMAT)
