import aiohttp


class BattleMetricsException(Exception):
    """The base class for all battlemetrics exceptions."""


class HTTPException(BattleMetricsException):
    """Thrown when an HTTP request fails.

    Attributes:
        status (int): The HTTP status code.

    """
    def __init__(self, response: aiohttp.ClientResponse, data, *args):
        self.status = response.status

        detail = None
        if isinstance(data, dict):
            errors = data.get('errors')
            if errors:
                detail = errors[0]['detail']
        else:
            detail = data
        self.detail = detail

        super().__init__(
            '{0.status} {0.reason}{1}'.format(
                response,
                f' ({detail})' if detail else ''
            ),
            *args
        )
