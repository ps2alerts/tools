import json
from time import sleep
from typing import Dict, List, Union
import requests
from argparse import ArgumentParser
from dateutil.parser import isoparse

from events import MetagameEvent, DeathEvent, FacilityControlEvent, VehicleDestroyEvent
from service import get_rabbit, RabbitConnection, RabbitService, Logger
from constants import MetagameEventType, MetagameEventState, Team

CENSUS = "https://census.daybreakgames.com/s:{}/get/ps2:v2/"

WORLD_EVENT = "world_event?after={}&before={}&world_id={}&c:limit=1000"
EVENT = "event?after={}&before={}&type=DEATH,KILL,VEHICLE_DESTROY&c:limit=1000"
OUTFIT_MEMBER = "outfit_member?character_id={}"

def main():
    parser = ArgumentParser(description="A tool to fix missed alerts from historical data")
    parser.add_argument("service_id", help="The service ID to use for census requests - no s:")
    parser.add_argument("after", type=str, help="The timestamp just before the alert started")
    parser.add_argument("before", type=str, help="The timestamp around when the alert ended")
    parser.add_argument("world", type=int, help="The world the alert was missed on")
    parser.add_argument("instance_id", type=int, help="The exact instance id to pull")
    parser.add_argument("--red-outfit-id", "-r", type=str, help="The red team's outfit id")
    parser.add_argument("--blue-outfit-id", "-b", type=str, help="The blue team's outfit id")
    args = parser.parse_args()

    before = 0
    after = 0
    try:
        before_date = isoparse(args.before)
        after_date = isoparse(args.after)
        before = int(before_date.timestamp())
        after = int(after_date.timestamp())
    except ValueError:
        before = int(args.before)
        after = int(args.after)

    world_events_resp = requests.get(CENSUS.format(args.service_id) + WORLD_EVENT.format(after, before, args.world))
    world_events: list = world_events_resp.json()["world_event_list"]
    world_events.sort(key=lambda x: int(x["timestamp"]))
    metagame_events = [
        event for event in world_events 
            if (event["event_type"] == "MetagameEvent" 
                and event["metagame_event_id"] == str(MetagameEventType.NEXUS_OUTFIT_WAR.value)
                and (args.instance_id is None or event["instance_id"] == str(args.instance_id)))]
    facility_events: Dict[str, List] = {}
    outfits: Dict[str, Dict[str, Union[Team, List[str]]]] = {"0": {"team": Team.NONE, "characters": []}}
    if args.red_outfit_id:
        outfits[args.red_outfit_id] = {"team": Team.RED, "characters": []}
        print(f"Outfit {args.red_outfit_id} is assigned team {outfits[args.red_outfit_id]['team'].name}")

    if args.blue_outfit_id:
        outfits[args.blue_outfit_id] = {"team": Team.BLUE, "characters": []}
        print(f"Outfit {args.blue_outfit_id} is assigned team {outfits[args.blue_outfit_id]['team'].name}")

    for event in metagame_events:
        if event["metagame_event_state"] == str(MetagameEventState.FINISHED.value):
            continue
        if event["instance_id"] not in facility_events:
            facility_events[event["instance_id"]] = []
        for facility_event in world_events:
            if facility_event["event_type"] != "FacilityControl":
                continue
            if facility_event["zone_id"] != event["zone_id"]:
                continue
            if facility_event["outfit_id"] not in outfits:
                team = Team(int(facility_event["faction_new"]))
                outfits[facility_event["outfit_id"]] = {"team": team, "characters": []}
                print(f"Outfit {facility_event['outfit_id']} is on team {outfits[facility_event['outfit_id']]['team'].name}")
            facility_events[event["instance_id"]].append(facility_event)

    zone_ids = {event["zone_id"] for event in metagame_events}
    
    print(f"Building combat events list for zone ids ({', '.join(zone_ids)})", end='', flush=True)
    combat_events_resp = requests.get(CENSUS.format(args.service_id) + EVENT.format(after, before))
    returned = combat_events_resp.json()["returned"]
    combat_events: list = [
        event for event in combat_events_resp.json()["event_list"] 
        if (event["world_id"] == str(args.world)
            and event["zone_id"] in zone_ids)
    ]
    while returned == 1000:
        print(".", end='', flush=True)
        last_event_timestamp = combat_events_resp.json()["event_list"][-1]["timestamp"]
        before = int(last_event_timestamp)
        combat_events_resp = requests.get(CENSUS.format(args.service_id) + EVENT.format(after, before))
        returned = combat_events_resp.json()["returned"]
        combat_events.extend([
            event for event in combat_events_resp.json()["event_list"] 
            if (event["world_id"] == str(args.world)
                and event["zone_id"] in zone_ids)
        ])
    combat_events.sort(key=lambda x: int(x["timestamp"]))
    print("\nAssigning teams...")

    found_characters: Dict[str, str] = {}
    for combat_event in combat_events:
        if combat_event["attacker_character_id"] not in found_characters and combat_event["attacker_character_id"] != "0":
            outfit_member_resp = requests.get(CENSUS.format(args.service_id) + OUTFIT_MEMBER.format(combat_event["attacker_character_id"]))
            if len(outfit_member_resp.json()["outfit_member_list"]) > 0:
                outfit_id = outfit_member_resp.json()["outfit_member_list"][0]["outfit_id"]
                if outfit_id in outfits:
                    outfits[outfit_id]["characters"].append(combat_event["attacker_character_id"])
                else:
                    print(f"Could not find outfit {outfit_id} in outfits in war?")
                found_characters[combat_event["attacker_character_id"]] = outfit_id
            else:
                found_characters[combat_event["attacker_character_id"]] = "0"

        if combat_event["character_id"] not in found_characters:
            outfit_member_resp = requests.get(CENSUS.format(args.service_id) + OUTFIT_MEMBER.format(combat_event["character_id"]))
            if len(outfit_member_resp.json()["outfit_member_list"]) > 0:
                outfit_id = outfit_member_resp.json()["outfit_member_list"][0]["outfit_id"]
                if outfit_id in outfits:
                    outfits[outfit_id]["characters"].append(combat_event["character_id"])
                else:
                    print(f"Could not find outfit {outfit_id} in outfits in war?")
                found_characters[combat_event["character_id"]] = outfit_id
            else:
                found_characters[combat_event["character_id"]] = "0"
        
        combat_event["attacker_team_id"] = str(outfits[found_characters[combat_event["attacker_character_id"]]]["team"].value)
        combat_event["team_id"] = str(outfits[found_characters[combat_event["character_id"]]]["team"].value)
        if "event_type" not in combat_event and combat_event["table_type"] in ("kills", "deaths"):
            combat_event["event_type"] = "Death"

    death_events: list = [
        event for event in combat_events if event["event_type"] == "Death"
    ]
    vehicle_destroy_events: list = [
        event for event in combat_events if event["event_type"] == "VehicleDestroy"
    ]
    print("Done.")

    with open("metagame_events.json", "w") as f:
        json.dump(metagame_events, f)
    with open("facility_events.json", "w") as f:
        json.dump(facility_events, f)
    with open("death_events.json", "w") as f:
        json.dump(death_events, f)
    with open("vehicle_destroy_events.json", "w") as f:
        json.dump(vehicle_destroy_events, f)


if __name__ == "__main__":
    main()