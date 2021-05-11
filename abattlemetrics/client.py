import asyncio
import logging
import json
from typing import Optional
from urllib.parse import quote

import aiohttp

from .errors import HTTPException
from .server import Server

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

                    remaining = int(r.headers['X-Rate-Limit-Remaining'])
                    if remaining == 0:
                        retry_after = float(r.headers['Retry-After'])
                        if self.sleep_on_ratelimit:
                            log.debug(f'Rate limited; retrying in {retry_after:.2f}')
                            await asyncio.sleep(retry_after)
                            log.debug('Done sleeping for rate limit, retrying...')
                            continue
                        else:
                            # unlock once rate limit is done
                            log.debug('Rate limited; raising exception')
                            lock.defer(retry_after)
                            raise HTTPException(r)

                    if r.status != 200:
                        raise HTTPException(r)

                    return data

    async def get_server_info(self, server_id: int, *, include_players=False):
        """Obtain server info given an ID.

        Args:
            server_id (int): The server's id.
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
