from enum import IntEnum
import requests
import auraxium
from auraxium import ps2
import asyncio
from argparse import ArgumentParser

class WORLD(IntEnum):
    CONNERY = 1
    MILLER = 10
    COBALT = 13
    EMERALD = 17
    JAEGER = 19
    SOLTECH = 40

async def main():
    parser = ArgumentParser()
    parser.add_argument("service_id", help="Your service id for accessing Census")
    parser.add_argument("--server-name", "-s", choices=["Emerald", "Connery", "Soltech", "Miller", "Cobalt"])
    parser.add_argument("--outfit-id", "-o", action="store_true", help="Output outfit ids in addition to tags")
    args = parser.parse_args()
    if not args.service_id.startswith("s:"):
        service_id = "s:" + args.service_id
    else:
        service_id = args.service_id
    outfit_signups = requests.get('https://census.lithafalcon.cc/get/ps2/outfit_war_registration?c:limit=1000').json()
    async with auraxium.Client(service_id=service_id) as client:
        for i in range(len(outfit_signups["outfit_war_registration_list"])):
            entry = outfit_signups["outfit_war_registration_list"][i]
            outfit = await client.get_by_id(ps2.Outfit, entry["outfit_id"])
            
            entry["outfit"] = outfit
    outfit_list = sorted(outfit_signups["outfit_war_registration_list"], key=lambda x: x["member_signup_count"], reverse=True)
    i = 0
    for entry in outfit_list:
        world_name = WORLD(int(entry['world_id'])).name.capitalize()
        if args.server_name is not None and args.server_name != world_name:
            continue
        print(f"{i + 1:3d}) {entry['outfit'].alias:>4s}{(' (' + str(entry['outfit_id']) + ')') if args.outfit_id else ''}: {entry['member_signup_count']}")
        i += 1

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())