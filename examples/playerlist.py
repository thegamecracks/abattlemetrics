import asyncio
import logging

import abattlemetrics as abm
import aiohttp

TOKEN = None

log = logging.getLogger("abattlemetrics")
log.setLevel(logging.DEBUG)
handler = logging.FileHandler("abattlemetrics.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
log.addHandler(handler)


async def main():
    async with aiohttp.ClientSession() as session:
        client = abm.BattleMetricsClient(session, TOKEN)
        # Get 5 random players currently online
        async for p in client.list_players(limit=5, is_online=True):
            print(p)


if __name__ == "__main__":
    asyncio.run(main())
