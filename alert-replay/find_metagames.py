# Find metagames for a supplied world and date ranges
# Usage: python find_metagames.py <service_id> <world> <start_date> <end_date>
# Example: python find_metagames.py fooServiceId 10 2023-01-01 2023-01-05

import argparse
import requests
import json
from datetime import datetime


# Function to validate the arguments
def validate_args(service_id, world, start_date, end_date):
    # Validate arguments
    if not service_id:
        print("Service ID must be supplied!")
        exit()

    if world not in [1, 10, 13, 17, 1000, 2000]:
        print("Invalid world!")
        exit()

    if not start_date or not end_date:
        print("Date range must be supplied!")
        exit()

    if start_date > end_date:
        print("Start date must be before end date!")
        exit()


# Parse Args
parser = argparse.ArgumentParser(
    description='Find metagames for a supplied world and date ranges'
)
parser.add_argument('service_id', type=str, help='Census service ID')
parser.add_argument('world', type=int, help='World number')
parser.add_argument('start_date', type=str, help='Start date')
parser.add_argument('end_date', type=str, help='End date')
args = parser.parse_args()
print(args)

validate_args(args.service_id, args.world, args.start_date, args.end_date)

# Send a request to Census to get the metagame data for the supplied world and date range
# The response is a JSON object with a list of metagame events
# Each metagame event has a timestamp, metagame instance ID, and metagame state

start_timestamp = int(datetime.strptime(args.start_date, '%Y-%m-%d').timestamp())
end_timestamp = int(datetime.strptime(args.end_date, '%Y-%m-%d').timestamp())

query = "https://census.daybreakgames.com/s:" + args.service_id + "/get/ps2:v2/world_event?type=metagame&world_id=" + str(args.world) + "&after=" + str(start_timestamp) + "&before=" + str(end_timestamp) + "&c:limit=1000"
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
