# Scans the available endpoints for Census and sees when data is first available, ticking in day increments since Nov 2019
# Make a http call to the Census API /event endpoint using event_types. Increment by 1 day (in unix) until we get a { "returned": >1 } response

import requests
from datetime import datetime
import json


event_types = [
  "ACHIEVEMENT", # Dodgy endpoint
  "BATTLE_RANK",
  "DEATH",
  "FACILITY_CHARACTER",
  "ITEM",
  "VEHICLE_DESTROY",
]

world_event_types = [
  "METAGAME",
  "FACILITY_CONTROL"
]

times = {
  "ACHIEVEMENT": 0,
  "BATTLE_RANK": 0,
  "DEATH": 0,
  "FACILITY_CHARACTER": 0,
  "FACILITY_CONTROL": 0,
  "ITEM": 0,
  "METAGAME": 0,
  "VEHICLE_DESTROY": 0,
}

def increment_timestamp(timestamp):
  print("Incrementing timestamp by 1 day")
  print(timestamp)
  return timestamp + 86400

def scanEndpoint(endpoint, types):
  # Convert into unix
  start_date = '2022-11-01'
  date_object = datetime.strptime(start_date, '%Y-%m-%d')
  start_timestamp = int(date_object.timestamp())

  for type in types:
    # Start at 1571094000 (2019-10-30 00:00:00 UTC), increment by 86400 (1 day) setting before and after until we get a response
    timestamp = start_timestamp
    error_count = 0

    while True:
      query = "https://census.daybreakgames.com/s:ps2alertsdotcom/get/ps2:v2/" + endpoint + "?type=" + type + "&after=" + str(timestamp) + "&before=" + str(timestamp + 86400) + "&c:limit=100000"
      print("Query: " + query)

      if error_count == 3:
        print("Too many errors, skipping type")
        times[type] = "ERROR"
        break

      date_object = datetime.fromtimestamp(timestamp)
      date_string = date_object.strftime("%Y-%m-%d")
      print("Trying on date " + date_string)

      # Handle exceptions as Census may crash
      try:
        r = requests.get(query, timeout=10)
        if r.status_code == 200:
          # Check if we got a returned key at all (we may have got server error)
          if "returned" in r.json():
            if r.json()["returned"] > 0:
              print(type + " " + str(timestamp))
              times[type] = date_string + ": " + str(r.json()["returned"]) + " records returned"
              break
            elif r.json()["returned"] == 0:
              print("No data returned")
            else:
              print("Unknown response, probably error")
              error_count += 1
          elif r.status_code != 200:
            print("Census API Error: " + str(r.status_code))
            error_count += 1

          timestamp = increment_timestamp(timestamp)
      except requests.exceptions.RequestException as e:
        print("Census API Error or timeout: " + str(e))
        timestamp = increment_timestamp(timestamp)
        error_count += 1

scanEndpoint('event', event_types)
scanEndpoint('world_event', world_event_types)

print(json.dumps(times, sort_keys=True, indent=4))
