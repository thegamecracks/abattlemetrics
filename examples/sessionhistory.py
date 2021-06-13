import asyncio
import logging

import abattlemetrics as abm
import aiohttp

PLAYER_ID = 1234

log = logging.getLogger('abattlemetrics')
log.setLevel(logging.DEBUG)
handler = logging.FileHandler('abattlemetrics.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)


async def main():
    async with aiohttp.ClientSession() as session:
        client = abm.BattleMetricsClient(session)
        async for s in client.get_player_session_history(PLAYER_ID, limit=1):
            print(s)


if __name__ == '__main__':
    asyncio.run(main())
