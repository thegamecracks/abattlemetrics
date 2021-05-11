import aiohttp


class BattleMetricsException(Exception):
    """The base class for all battlemetrics exceptions."""


class HTTPException(BattleMetricsException):
    """Thrown when an HTTP request fails.

    Attributes:
        status (int): The HTTP status code.

    """
    def __init__(self, response: aiohttp.ClientResponse):
        self.status = response.status
        super().__init__('{0.status} {0.reason}'.format(response))
