import asyncio
import logging

import aiohttp

import abattlemetrics as abm

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.FileHandler('abattlemetrics.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)


async def main():
    async with aiohttp.ClientSession() as session:
        client = abm.BattleMetricsClient(session)
        server = await client.get_server_info(1234, include_players=True)
        print(server)


if __name__ == '__main__':
    asyncio.run(main())
