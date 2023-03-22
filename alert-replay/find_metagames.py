# Find metagames for a supplied world and date ranges
# Usage: python find_metagames.py <world> <start_date> <end_date>
# Example: python find_metagames.py 1 2023-01-01 2023-01-05

import argparse
import requests
import json

service_id = "ps2alertsdotcom"

parser = argparse.ArgumentParser(
    description='Find metagames for a supplied world and date ranges'
)
parser.add_argument('world', type=int, help='World number')
parser.add_argument('start_timestamp', type=int, help='Start unix timestamp')
parser.add_argument('end_timestamp', type=int, help='End unix timestamp')

args = parser.parse_args()

# Validate arguments
if args.world not in [1, 10, 13, 17, 1000, 2000]:
    print("Invalid world!")
    exit()

if not args.start_timestamp or not args.end_timestamp:
    print("Timestamps must be supplied!")
    exit()

if args.start_timestamp > args.start_timestamp:
    print("Start timestamp must be before end timestamp!")
    exit()

# Send a request to Census to get the metagame data for the supplied world and date range
# The response is a JSON object with a list of metagame events
# Each metagame event has a timestamp, metagame instance ID, and metagame state

query = "https://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2/world_event?type=metagame&world_id=" + str(args.world) + "&after=" + str(args.start_timestamp) + "&before=" + str(args.end_timestamp) + "&c:limit=10000"
print(query)
r = requests.get(query)

if r.status_code != 200:
    print("Error retrieving metagame data!")
    exit()

# Array of metagame events with the timestamp as the key
metagame_events = {}

# Loop through the metagame events

for metagame_event in r.json()["world_event_list"]:
    # Key comprises the world id and the unique metagame instance id which is unique per world
    key = metagame_event["world_id"] + "_" + metagame_event["instance_id"]

    # If the metagame event already exists, get the data
    if key in metagame_events:
        data = metagame_events[key]
    else:
        data = {
            'instance_id': int(metagame_event["instance_id"]),
            'world_id': int(metagame_event["world_id"]),
            'zone_id': int(metagame_event["zone_id"]),
            'metagame_event_id': int(metagame_event["metagame_event_id"]),  # https://github.com/ps2alerts/constants/blob/main/metagameEventType.ts for a full list
            'started': 0,
            'ended': 0
        }

    # If the metagame event already exists, update the start and end timestamps
    if metagame_event["metagame_event_state_name"] == "started":
        data['started'] = int(metagame_event["timestamp"])
    else:
        data['ended'] = int(metagame_event["timestamp"])

    # Set the data again
    metagame_events[key] = data

print(json.dumps(metagame_events, indent=4, sort_keys=True))

print("Found " + str(len(metagame_events)) + " alerts!")
