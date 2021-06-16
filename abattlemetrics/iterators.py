import collections
import logging
from typing import List, Literal, Optional, Union
import urllib.parse as urlparse

from .player import Player
from .session import Session
from .server import Server

__all__ = ('AsyncIterator', 'AsyncPlayerListIterator', 'AsyncSessionIterator')

log = logging.getLogger(__name__)


def _convert_params_to_array(params: dict) -> Union[dict, list]:
    """Convert a dictionary to a list of key-value pairs, unpacking
    list values to their own keys. If none of the values are a list,
    returns the dictionary untouched.
    """
    if not any(isinstance(v, list) for v in params.values()):
        return params

    new = []
    for k, v in params.items():
        if isinstance(v, list):
            for v_v in v:
                new.append((k, v_v))
        else:
            new.append((k, v))
    return new


class AsyncIterator:
    async def flatten(self):
        x = []
        async for item in self:
            x.append(item)
        return x

    async def next(self):
        raise NotImplementedError

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.next()


class AsyncPaginatedIterator(AsyncIterator):
    _MAX_SIZE = 100

    def __init__(self, client, route, limit, params):
        self._client = client
        self._route = route
        self._limit = limit
        self._params = params
        self._current_page = None

    def _get_next_params(self, r: dict) -> Optional[dict]:
        params = r['links'].get('next')
        if params:
            return urlparse.parse_qs(urlparse.urlparse(params).query)
        return

    async def _request_page(self, params: Union[dict, list]):
        params = _convert_params_to_array(params)
        res = await self._client._request(self._route, params=params)
        page = await self._parse_response(res)

        params = None
        if page:
            params = self._get_next_params(res)

        self._limit -= len(page)
        if params and self._limit <= 0:
            params = None

        page.reverse()
        self._current_page = page
        self._params = params

    async def _parse_response(self, r: dict) -> List[object]:
        raise NotImplementedError

    async def next(self):
        if self._current_page:
            return self._current_page.pop()
        elif self._params is not None:
            self._params['page[size]'] = min(self._limit, self._MAX_SIZE)
            await self._request_page(self._params)

        if self._current_page:
            return self._current_page.pop()
        else:
            raise StopAsyncIteration


class AsyncPlayerListIterator(AsyncPaginatedIterator):
    def __init__(self, client, limit, params):
        route = client._Route('GET', '/players')
        super().__init__(client, route, limit, params)

    async def _request_page(self, params):
        log.debug('Requesting %d players listed', params['page[size]'])
        await super()._request_page(params)

    async def _parse_response(self, r) -> List[Player]:
        identifiers = collections.defaultdict(list)
        for payload in r['included']:
            if payload['type'] == 'identifier':
                p_id = int(payload['relationships']['player']['data']['id'])
                identifiers[p_id].append(payload)

        return [
            Player(
                payload,
                identifiers.get(int(payload['id']), None)
            )
            for payload in r['data']
        ]


class AsyncSessionIterator(AsyncPaginatedIterator):
    def __init__(self, client, limit, player_id, params):
        route = client._Route(
            'GET', '/players/{player_id}/relationships/sessions',
            player_id=player_id
        )
        super().__init__(client, route, limit, params)

    async def _request_page(self, params):
        log.debug('Requesting %d sessions', params['page[size]'])
        await super()._request_page(params)

    async def _parse_response(self, r) -> List[Session]:
        servers = {
            payload['attributes']['id']: Server(payload)
            for payload in r['included']
            if payload['type'] == 'server'
        }

        page = []
        for payload in r['data']:
            session = Session(payload)

            server = servers.get(session.server_id)
            if server is not None:
                super(Session, session).__setattr__('server', server)

            page.append(session)

        return page
