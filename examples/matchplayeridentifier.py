import asyncio
import datetime
import logging

import abattlemetrics as abm
import aiohttp

TOKEN = '<Your token here>'
PLAYER_ID = 1234
PLAYER_ID_TYPE = abm.IdentifierType.STEAM_ID

log = logging.getLogger('abattlemetrics')
log.setLevel(logging.DEBUG)
handler = logging.FileHandler('abattlemetrics.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
log.addHandler(handler)


async def main():
    async with aiohttp.ClientSession() as session:
        client = abm.BattleMetricsClient(session, TOKEN)
        player_id = await client.match_player(PLAYER_ID, PLAYER_ID_TYPE)
        if player_id:
            player = await client.get_player_info(player_id)
            print(player)
        else:
            print('Player not found')


if __name__ == '__main__':
    asyncio.run(main())
