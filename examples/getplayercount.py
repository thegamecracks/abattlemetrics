import asyncio
import datetime
import logging
from pprint import pprint

import abattlemetrics as abm
import aiohttp

log = logging.getLogger('abattlemetrics')
log.setLevel(logging.DEBUG)
handler = logging.FileHandler('abattlemetrics.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)


async def main():
    async with aiohttp.ClientSession() as session:
        client = abm.BattleMetricsClient(session)
        # Get the player count history in the last hour
        start = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        stop = datetime.datetime.now().astimezone()
        datapoints = await client.get_player_count_history(1234, start=start, stop=stop)
        pprint(datapoints)


if __name__ == '__main__':
    asyncio.run(main())
