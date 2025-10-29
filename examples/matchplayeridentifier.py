import asyncio
import logging

import abattlemetrics as abm
import aiohttp

TOKEN = "<Your token here>"
PLAYER_ID = 1234
PLAYER_ID_TYPE = abm.IdentifierType.STEAM_ID

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
        results = await client.match_players(PLAYER_ID, type=PLAYER_ID_TYPE)
        bm_id = results[PLAYER_ID]
        if bm_id is not None:
            player = await client.get_player_info(bm_id)
            print(player)
        else:
            print("Player not found")


if __name__ == "__main__":
    asyncio.run(main())
