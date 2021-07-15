import datetime

import dateutil.parser


def isoify_datetime(dt: datetime.datetime) -> str:
    """Turn a datetime into a ISO formatted string in UTC suitable
    for parameters."""
    dt = dt.astimezone(datetime.timezone.utc)
    return dt.replace(microsecond=0, tzinfo=None).isoformat() + 'Z'


def parse_datetime(date_string: str) -> datetime.datetime:
    """Parse a datetime given by battlemetrics."""
    dt = dateutil.parser.isoparse(date_string)
    if dt.tzinfo:
        return dt.astimezone(datetime.timezone.utc)
    return dt.replace(tzinfo=datetime.timezone.utc)
