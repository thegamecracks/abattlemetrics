import asyncio
import datetime
import logging
from pprint import pprint

import abattlemetrics as abm
import aiohttp

PLAYER_ID = 1234
SERVER_ID = 1234

log = logging.getLogger("abattlemetrics")
log.setLevel(logging.DEBUG)
handler = logging.FileHandler("abattlemetrics.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
log.addHandler(handler)


async def main():
    async with aiohttp.ClientSession() as session:
        client = abm.BattleMetricsClient(session)
        # Get the time played history in the last week
        stop = datetime.datetime.now()
        start = stop - datetime.timedelta(weeks=1)
        datapoints = await client.get_player_time_played_history(
            PLAYER_ID,
            SERVER_ID,
            start=start,
            stop=stop,
        )
        pprint(datapoints)


if __name__ == "__main__":
    asyncio.run(main())
