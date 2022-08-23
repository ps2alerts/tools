from dataclasses import dataclass, is_dataclass, asdict
from enum import IntEnum
import requests
import auraxium
from auraxium import ps2
import asyncio
from argparse import ArgumentParser
import json

class WORLD(IntEnum):
    CONNERY = 1
    MILLER = 10
    COBALT = 13
    EMERALD = 17
    JAEGER = 19
    SOLTECH = 40

@dataclass
class outfit:
    id: int
    alias: str
    name: str
    member_count: int

class OutfitJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)

async def main():
    parser = ArgumentParser()
    parser.add_argument("service_id", help="Your service id for accessing Census")
    parser.add_argument("server_name", choices=["Emerald", "Connery", "Soltech", "Miller", "Cobalt"])
    parser.add_argument("--outfit-id", "-o", action="store_true", help="Output outfit ids in addition to tags")
    args = parser.parse_args()
    if not args.service_id.startswith("s:"):
        service_id = "s:" + args.service_id
    else:
        service_id = args.service_id
    
    world = int(WORLD[args.server_name.upper()])
    outfit_war = requests.get(f'https://census.lithafalcon.cc/get/ps2/outfit_war?world_id={world}&c:show=outfit_war_id,world_id&c:join=outfit_war_rounds^show:primary_round_id(outfit_war_ranking^on:primary_round_id^to:round_id)').json()
    outfit_war_list = sorted(outfit_war["outfit_war_list"], key=lambda x: x["outfit_war_id_join_outfit_war_rounds"]["primary_round_id_join_outfit_war_ranking"]["ranking_parameters"]["GlobalRank"])
    async with auraxium.Client(service_id=service_id) as client:
        for i in range(len(outfit_war_list)):
            entry = outfit_war_list[i]
            census_outfit = await client.get_by_id(ps2.Outfit, entry["outfit_war_id_join_outfit_war_rounds"]["primary_round_id_join_outfit_war_ranking"]["outfit_id"])
            entry["outfit"] = outfit(census_outfit.id, census_outfit.alias, census_outfit.name, census_outfit.member_count)
    
    matches = [
        ({
            "order": outfit_war_list[i]["outfit_war_id_join_outfit_war_rounds"]["primary_round_id_join_outfit_war_ranking"]["order"],
            "outfit": outfit_war_list[i]["outfit"], 
            "ranking_parameters": outfit_war_list[i]["outfit_war_id_join_outfit_war_rounds"]["primary_round_id_join_outfit_war_ranking"]["ranking_parameters"]
        }, {
            "order": outfit_war_list[i + 1]["outfit_war_id_join_outfit_war_rounds"]["primary_round_id_join_outfit_war_ranking"]["order"],
            "outfit": outfit_war_list[i + 1]["outfit"], 
            "ranking_parameters": outfit_war_list[i + 1]["outfit_war_id_join_outfit_war_rounds"]["primary_round_id_join_outfit_war_ranking"]["ranking_parameters"]
        }) for i in range(0, len(outfit_war_list), 2) if (i + 1) < len(outfit_war_list)
    ]
    with open(f"{args.server_name}_matches.json", "w") as f:
        json.dump(matches, f, cls=OutfitJSONEncoder)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())