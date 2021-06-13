import logging
from typing import Optional, Union
import urllib.parse as urlparse

from .session import Session
from .server import Server

log = logging.getLogger(__name__)


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
    
class AsyncSessionIterator(AsyncIterator):
    def __init__(
            self, client, player_id, limit, organization_ids, server_ids,
            include_servers):
        self._client = client
        self._limit = limit
        self._organization_ids = organization_ids
        self._server_ids = server_ids
        self._include_servers = include_servers

        self._route = client._Route(
            'GET', '/players/{player_id}/relationships/sessions',
            player_id=player_id
        )
        self._current_page = []
        self._params: Optional[Union[dict, False]] = None

    async def _parse_response(self, r):
        params = r['links'].get('next', False)
        if params:
            params = urlparse.parse_qs(urlparse.urlparse(params).query)

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

        # NOTE: is this needed? i.e. does battlemetrics guarantee that
        # next won't be provided if no data is given?
        if not page:
            params = False

        return page, params

    async def next(self):
        async def request_page(params):
            log.debug('Requesting %d sessions', params['page[size]'])
            res = await self._client._request(self._route, params=params)
            page, params = await self._parse_response(res)

            self._limit -= len(page)
            if params:
                if self._limit > 0:
                    # Update page size so we don't query excess sessions
                    params['page[size]'] = min(self._limit, 100)
                else:
                    # Stop making more requests after this page
                    params = False

            page.reverse()
            self._current_page = page
            self._params = params

        if self._current_page:
            return self._current_page.pop()
        elif self._params:
            # Next page
            await request_page(self._params)
        elif self._params is not False:
            # Initial request
            params = {
                'page[size]': min(self._limit, 100)
            }

            if self._organization_ids:
                params['filter[organizations]'] = ','.join([
                    str(n) for n in self._organization_ids])
            if self._server_ids:
                params['filter[servers]'] = ','.join([
                    str(n) for n in self._server_ids])

            include = []
            if self._include_servers:
                include.append('server')
            include = ','.join(include)
            if include:
                params['include'] = include

            await request_page(params)

        if self._current_page:
            return self._current_page.pop()
        else:
            raise StopAsyncIteration
