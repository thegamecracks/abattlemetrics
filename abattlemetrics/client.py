import asyncio
import datetime
import functools
import logging
import json
from typing import List, Optional, Union
from urllib.parse import quote

import aiohttp

from .datapoint import DataPoint, Resolution
from .errors import HTTPException
from .server import Server
from . import utils

log = logging.getLogger(__name__)


async def _json_or_text(response):
    text = await response.text(encoding='utf-8')
    if response.headers.get('content-type') == 'application/json':
        return json.loads(text)
    return text


class _MaybeUnlock:
    def __init__(self, lock: asyncio.Lock):
        self.lock = lock
        self._unlock = True

    async def __aenter__(self):
        await self.lock.acquire()
        return self

    def defer(self, unlock_after: Optional[float] = None):
        self._unlock = False
        if unlock_after is not None:
            loop = asyncio.get_running_loop()
            return loop.call_later(unlock_after, self.lock.release)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._unlock:
            self.lock.release()


class _Route:
    BASE = 'https://api.battlemetrics.com'

    def __init__(self, method, path, **params):
        self.path = path
        self.method = method
        url = self.BASE + path
        if params:
            url = url.format(**{k: quote(v) if isinstance(v, str) else v for k, v in params.items()})
        self.url = url


def alias_param(name, alias):
    """Alias a keyword parameter in a function.
    Throws a TypeError when a value is given for both the
    original kwarg and the alias.
    """
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            alias_value = kwargs.get(alias)
            if alias_value:
                if name in kwargs:
                    raise TypeError(f'Cannot pass both {name!r} and {alias!r} in call')
                kwargs[name] = alias_value
            return func(*args, **kwargs)
        return wrapper
    return deco


class BattleMetricsClient:
    """An interface to the battlemetrics API.

    Args:
        session (aiohttp.ClientSession): The session to make requests with.
        token (Optional[str]): An optional authorization token to use when
            making requests.
        sleep_on_ratelimit (bool): Whether ratelimits should be handled by
            sleeping or raising an error.

    """
    def __init__(
            self, session: aiohttp.ClientSession, token: Optional[str] = None,
            *, sleep_on_ratelimit: bool = True):
        self.session = session
        self.token = token
        self.sleep_on_ratelimit = sleep_on_ratelimit
        self._reqlock = asyncio.Lock()

    async def _request(self, route: _Route, *, params: Optional[dict] = None):
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        if params is None:
            params = {}

        async with _MaybeUnlock(self._reqlock) as lock:
            for tries in range(5):
                async with self.session.request(
                        route.method, route.url,
                        headers=headers, params=params) as r:
                    log.debug(f'{route.method} {route.url} returned {r.status}')
                    data = await _json_or_text(r)

                    retry_after = r.headers.get('Retry-After', 0)
                    # NOTE: battlemetrics doesn't always give
                    # X-Rate-Limit-Remaining header
                    if retry_after:
                        if self.sleep_on_ratelimit:
                            log.warning(f'Rate limited; retrying in {retry_after:.2f}')
                            await asyncio.sleep(retry_after)
                            log.debug('Done sleeping for rate limit, retrying...')
                            continue
                        else:
                            e = HTTPException(r)
                            # unlock once rate limit is done
                            log.warning(
                                'Rate limited; sleep_on_ratelimit '
                                'is True, raising exception', exc_info=e
                            )
                            lock.defer(retry_after)
                            raise e

                    if r.status != 200:
                        e = HTTPException(r)
                        log.exception(
                            'Response %d caused with:\nHeaders: %s\nParams: %s',
                            r.status, headers, params, exc_info=e
                        )
                        raise e

                    return data

            # No more retries left
            raise HTTPException(r)

    @alias_param('stop', 'before')
    @alias_param('start', 'after')
    async def get_player_count_history(
            self, server_id: int, *,
            start: datetime.datetime = None, stop: datetime.datetime = None,
            resolution: Optional[Resolution] = Resolution.RAW
        ) -> List[DataPoint]:
        """Obtain a server's player count history.

        Args:
            server_id (int): The server's ID.
            start (datetime.datetime):
                Get the player count history after this time.
                If naive, assumes time is in UTC.
                This parameter has "after" as an alias.
            stop (datetime.datetime):
                Get the player count history before this time.
                If naive, assumes time is in UTC.
                This parameter has "before" as an alias.
            resolution (Optional[Resolution]):
                The resolution of the data points. If raw, the data points
                will only have value provided. Any other option will provide
                value, min, and max.

        Returns:
            List[DataPoint]: A list of data points sorted by timestamp.

        """
        r = _Route('GET', '/servers/{server_id}/player-count-history', server_id=server_id)

        params = {
            'start': utils.isoify_datetime(start),
            'stop': utils.isoify_datetime(stop),
            'resolution': resolution.value
        }

        payload = await self._request(r, params=params)
        data = payload['data']

        datapoints = [DataPoint(d['attributes']) for d in data]
        datapoints.sort(key=lambda dp: dp.timestamp)

        return datapoints

    @alias_param('stop', 'before')
    @alias_param('start', 'after')
    async def get_player_time_played_history(
            self, player_id: int, server_id: int, *,
            start: datetime.datetime = None,
            stop: datetime.datetime = None
        ) -> List[DataPoint]:
        """Obtain a player's time played history for a server.
        The values of each datapoint are in seconds.

        Start and stop are truncated to the date.

        Args:
            player_id (int): The player's ID.
            server_id (int): The server ID.
            start (datetime.datetime):
                Get the time played history after this time.
                If naive, assumes time is in UTC.
                This parameter has "after" as an alias.
            stop (datetime.datetime):
                Get the time played history before this time.
                If naive, assumes time is in UTC.
                This parameter has "before" as an alias.

        Returns:
            List[DataPoint]: A list of data points sorted by timestamp.

        """
        r = _Route('GET', '/players/{player_id}/time-played-history/{server_id}',
                   player_id=player_id, server_id=server_id)

        params = {
            'start': utils.isoify_datetime(start),
            'stop': utils.isoify_datetime(stop)
        }

        payload = await self._request(r, params=params)
        data = payload['data']

        datapoints = [DataPoint(d['attributes']) for d in data]
        datapoints.sort(key=lambda dp: dp.timestamp)

        return datapoints

    async def get_server_info(
            self, server_id: int, *, include_players=False
        ) -> Server:
        """Obtain server info given an ID.

        Args:
            server_id (int): The server's ID.
            include_players (bool): Whether to also fetch player data.
                This affects the `players` attribute.

        """
        r = _Route('GET', '/servers/{server_id}', server_id=server_id)

        params = {}

        include = []
        if include_players:
            include.append('player')

        include = ','.join(include)
        if include:
            params['include'] = include

        return Server(await self._request(r, params=params))
