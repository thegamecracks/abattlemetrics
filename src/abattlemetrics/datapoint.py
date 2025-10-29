import datetime
import enum
from dataclasses import dataclass, field
from typing import Optional

from .mixins import PayloadIniter
from . import utils

__all__ = ('DataPoint', 'Resolution')


class Resolution(enum.Enum):
    """The resolution to use when querying DataPoints."""
    RAW = 'raw'
    SEVEN_DAYS = 30
    THIRTY_DAYS = 60
    SIX_MONTHS = 1440


@dataclass(frozen=True, init=False, repr=False)
class DataPoint(PayloadIniter):
    """A data point of a time series.

    group (Optional[int]): If multiple groups of metrics were requested,
        this will be the index of the corresponding group.
    max (Optional[int]): The minimum value of the datapoint if relevant.
        This is usually provided when resolution is not raw.
    min (Optional[int]): The minimum value of the datapoint if relevant.
        This is usually provided when resolution is not raw.
    name (Optional[str]): The name of the metric.
        Only provided when more than one metric is requested.
    timestamp (datetime.datetime):
        The data point's timestamp as an aware datetime.
    value (int): The value of the data point.

    """
    __init_attrs = ('group', 'min', 'max', 'name', 'value')

    group: Optional[int]
    min: Optional[int]
    max: Optional[int]
    name: Optional[str]
    timestamp: datetime.datetime
    value: int

    def __init__(self, payload):
        self.__init_attrs__(payload, self.__init_attrs, required=False)
        super().__setattr__('timestamp', utils.parse_datetime(payload['timestamp']))
        assert self.value is not None, 'payload is missing "value"'

    def __repr__(self):
        fields = self.__dict__
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join([
                f'{name}={value!r}' for name, value in fields.items()
                if value is not None and not name.startswith('_')
            ])
        )
