from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum

import json
import math
from time import sleep
from urlpath import URL
import random
from typing import List, Optional
import requests
from requests.auth import HTTPBasicAuth

class AlertState(IntEnum):
    STARTING = 0
    STARTED = 1
    ENDED = 2

class Team(IntEnum):
    NONE = 0
    BLUE = 2
    RED = 3

@dataclass
class MapControl:
    vs: float
    nc: float
    tr: float
    cutoff: float
    out_of_play: float

    def to_json(self) -> dict:
        return {
            "vs": self.vs,
            "nc": self.nc,
            "tr": self.tr,
            "cutoff": self.cutoff,
            "outOfPlay": self.out_of_play
        }

@dataclass
class FacilityControl:
    instance: str
    facility_id: int
    timestamp: datetime
    old_faction: int
    new_faction: int
    duration_held: int = 0
    is_initial: bool = False
    is_defence: bool = False
    outfit_captured: Optional[int] = None
    map_control: Optional[MapControl] = None

    def to_json(self) -> dict:
        return {
            "instance": self.instance,
            "facility": self.facility_id,
            "timestamp": self.timestamp.isoformat(),
            "oldFaction": self.old_faction,
            "newFaction": self.new_faction,
            "durationHeld": self.duration_held,
            "isInitial": self.is_initial,
            "isDefence": self.is_defence,
            "outfitCaptured": str(self.outfit_captured),
            "mapControl": self.map_control.to_json() if self.map_control is not None else None
        }

@dataclass
class MetagameResult:
    vs: float
    nc: float
    tr: float
    cutoff: float
    out_of_play: float
    victor: Optional[Team] = None
    draw: bool = False
    per_base_percentage: float = 100/9

    def to_json(self) -> dict:
        return {
            "vs": self.vs,
            "nc": self.nc,
            "tr": self.tr,
            "cutoff": self.cutoff,
            "outOfPlay": self.out_of_play,
            "victor": self.victor,
            "draw": self.draw,
            "perBasePercentage": self.per_base_percentage,
        }

@dataclass
class MetagameEvent:
    world: int
    zone: int
    zone_instance: int
    census_id: int
    time_started: datetime
    time_ended: Optional[datetime] = None
    _type: int = 227 # Nexus Outfit War
    result: MetagameResult = MetagameResult(0, 33, 33, 0, 34)
    duration: int = 1000 * 60 * 45 # 45 minute alert
    state: AlertState = AlertState.STARTED
    map_version: str = "1.0"
    __instance_id: str = None

    def to_json(self) -> dict:
        return {
            "instanceId": self.instance_id(),
            "world": self.world,
            "timeStarted": self.time_started.isoformat(),
            "timeEnded": self.time_ended.isoformat() if self.time_ended is not None else None,
            "result": self.result.to_json() if self.result is not None else None,
            "zone": self.zone,
            "zoneInstanceId": self.zone_instance,
            "censusInstanceId": self.census_id,
            "censusMetagameEventType": self._type,
            "duration": self.duration,
            "state": self.state,
            "bracket": 5,
            "features": {
                "captureHistory": True
            },
            "mapVersion": self.map_version
        }
    
    def instance_id(self) -> str:
        if self.__instance_id is None:
            self.__instance_id = f"{self.world}-{self.census_id:05d}"
        return self.__instance_id

BASE = URL("https://dev.api.ps2alerts.com")
AUTH = HTTPBasicAuth("ps2alerts", "foobar") # default dev auth

INIT_BLUE_REGIONS = [310560, 310610, 310550, 310520]
INIT_RED_REGIONS  = [310570, 310600, 310540, 310510]
INIT_NS_REGIONS   = [310530, 310500, 310590]
BLUE_OUTFIT = 37571208657592881
RED_OUTFIT = 37570391403474491
MAX_CAPTURES = 20

class Map:
    def __init__(self, zone_id: int, version: str = "1.0"):
        response = requests.get(str(BASE / "census" / "regions" / str(zone_id) / version))
        assert 200 <= response.status_code <= 299, "Failed to retrieve map data"
        data = response.json()
        self._regions = {}
        for region in data["map_region_list"]:
            self._regions[region["facility_id"]] = {
                "name": region["facility_name"],
                "links": [link["facility_id_b"] for link in region["facility_links"]],
                "faction": Team.NONE
            }
        
        for facility_id in self._regions:
            for link_id in self._regions[facility_id]["links"]:
                if facility_id not in self._regions[link_id]["links"]:
                    self._regions[link_id]["links"].append(facility_id)
    
    def capture(self, facility_id: int, team: Team):
        self._regions[str(facility_id)]["faction"] = team
    
    def get_capturable(self, team: Team) -> List[int]:
        to_return = []
        for facility_id in self._regions:
            if facility_id in ["310560", "310570"]:
                # warpgates are not capturable
                continue
            if self._regions[facility_id]["faction"] == team:
                # Cannot capture your own bases
                continue
            for link_id in self._regions[facility_id]["links"]:
                if self._regions[link_id]["faction"] == team:
                    # Have a connected base? Capturable
                    to_return.append(int(facility_id))
        return to_return
    
    def get_region(self, facility_id: int):
        if str(facility_id) not in self._regions:
            return None
        return self._regions[str(facility_id)]
    
    def percentages(self) -> MapControl:
        red_bases = 0
        blue_bases = 0
        ns_bases = 0
        for facility_id in self._regions:
            if facility_id in ["310560", "310570"]:
                continue
            if self._regions[facility_id]["faction"] == Team.RED:
                red_bases += 1
            elif self._regions[facility_id]["faction"] == Team.BLUE:
                blue_bases += 1
            elif self._regions[facility_id]["faction"] == Team.NONE:
                ns_bases += 1
        return MapControl(
            0,
            int(100 * blue_bases / (len(self._regions) - 2)), 
            int(100 * red_bases / (len(self._regions) - 2)),
            0,
            int(100 * ns_bases / (len(self._regions) - 2))
        )

def nexus_alert(world: int, instance: int):
    zone_id = 10
    event = MetagameEvent(world, zone_id, instance, random.randint(10000, 99999), datetime.utcnow())
    response = requests.post(str(BASE / "outfit-wars"), json=event.to_json(), auth=AUTH)
    try:
        assert 200 <= response.status_code <= 299, "Failed to create new instance"

        nexus = Map(zone_id)

        for facility_id in INIT_BLUE_REGIONS:
            capture = FacilityControl(
                event.instance_id(), 
                facility_id, 
                datetime.utcnow(), 
                old_faction=Team.BLUE, 
                new_faction=Team.BLUE, 
                is_initial=True
            )
            nexus.capture(facility_id, Team.BLUE)
            response = requests.post(
                str(BASE / "instance-entries" / event.instance_id() / "facility"),
                json=capture.to_json(),
                auth=AUTH
            )
            assert 200 <= response.status_code <= 299, "Failed to initialize Blue Regions"
        
        for facility_id in INIT_RED_REGIONS:
            capture = FacilityControl(
                event.instance_id(), 
                facility_id, 
                datetime.utcnow(), 
                old_faction=Team.RED, 
                new_faction=Team.RED, 
                is_initial=True
            )
            nexus.capture(facility_id, Team.RED)
            response = requests.post(
                str(BASE / "instance-entries" / event.instance_id() / "facility"),
                json=capture.to_json(),
                auth=AUTH
            )
            assert 200 <= response.status_code <= 299, "Failed to initialize Red Regions"
        
        for facility_id in INIT_NS_REGIONS:
            capture = FacilityControl(
                event.instance_id(), 
                facility_id, 
                datetime.utcnow(), 
                old_faction=Team.NONE, 
                new_faction=Team.NONE, 
                is_initial=True
            )
            nexus.capture(facility_id, Team.NONE)
            response = requests.post(
                str(BASE / "instance-entries" / event.instance_id() / "facility"),
                json=capture.to_json(),
                auth=AUTH
            )
            assert 200 <= response.status_code <= 299, "Failed to initialize Blue Regions"

        to_capture = 0
        captures = MAX_CAPTURES
        while to_capture not in [310610, 310600] and captures > 0:
            team = random.choice([Team.BLUE, Team.RED])
            to_capture = random.choice(nexus.get_capturable(team))
            old_faction = nexus.get_region(to_capture)["faction"]
            nexus.capture(to_capture, team)
            capture = FacilityControl(
                event.instance_id(), 
                to_capture, 
                datetime.utcnow(), 
                old_faction=old_faction, 
                new_faction=team,
                outfit_captured=(RED_OUTFIT if team == Team.RED else BLUE_OUTFIT),
                map_control=nexus.percentages()
            )
            response = requests.post(
                str(BASE / "instance-entries" / event.instance_id() / "facility"),
                json=capture.to_json(),
                auth=AUTH
            )
            if not (200 <= response.status_code <= 299):
                print(f"Error {response.status_code}: {response.content}")
                print(capture.to_json())
                assert False
            
            captures -= 1
            sleep(5)
        
        end_control = nexus.percentages()
        winner = Team.RED if end_control.tr > 50 else Team.BLUE
        event.result.nc = end_control.nc
        event.result.tr = end_control.tr
        event.result.out_of_play = end_control.out_of_play
        event.result.victor = winner
    finally:
        event.time_ended = datetime.utcnow()
        event.state = AlertState.ENDED
        data = event.to_json()
        del data["world"]
        del data["timeStarted"]
        del data["zone"]
        del data["zoneInstanceId"]
        del data["censusInstanceId"]
        del data["censusMetagameEventType"]
        del data["duration"]
        del data["features"]
        del data["mapVersion"]
        response = requests.put(str(BASE / "outfit-wars" / event.instance_id()), json=event.to_json(), auth=AUTH)
        if not (200 <= response.status_code <= 299):
            print(f"Error {response.status_code}: {response.content}")
            print(data)



# Simple simulator that fakes an alert on Nexus with a bunch of random (possible) captures
#   Basically intended to test out various scenarios that could happen with outfit wars
def main():
    world = 1
    instance = random.randint(0, 0xFFFF)
    print(f"Starting alert on world {world}, zone instance {instance}")
    nexus_alert(world, instance)
    print(f"Finished alert on world {world}, zone instance {instance}")

if __name__ == "__main__":
    main()