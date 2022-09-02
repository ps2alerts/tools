from pathlib import Path
import requests
from typing import Dict, List

import AppConfig
from constants.OutfitWars import Nexus
from constants import Team
from dataclass import MapControl
from .Region import Region

class NexusMap:
    def __init__(self, zone_id: int, version: str = "1.0"):
        response = requests.get(str(AppConfig.apiBaseUrl / "census" / "regions" / str(zone_id) / version), verify=Path("~/ps2alerts/certs/CA.pem").expanduser())
        assert 200 <= response.status_code <= 299, "Failed to retrieve map data"
        data = response.json()
        self._region_counts = {
            Team.NONE: 0,
            Team.BLUE: 0,
            Team.RED: 0
        }
        self._regions: Dict[str, Region] = {}
        for region in data["map_region_list"]:
            self._regions[region["facility_id"]] = Region(
                region["facility_name"], 
                [link["facility_id_b"] for link in region["facility_links"]],
                (Team.BLUE if int(region["facility_id"]) in Nexus.INIT_BLUE_REGIONS
                       else Team.RED  if int(region["facility_id"]) in Nexus.INIT_RED_REGIONS
                       else Team.NONE)
            )
            self._region_counts[self._regions[region["facility_id"]].faction] += 1

        for facility_id in self._regions:
            for link_id in self._regions[facility_id].links:
                if facility_id not in self._regions[link_id].links:
                    self._regions[link_id].links.append(facility_id)

    def capture(self, facility_id: int, team: Team):
        self._region_counts[self._regions[str(facility_id)].faction] -= 1
        self._region_counts[team] += 1
        self._regions[str(facility_id)].faction = team

    def count(self, team: Team):
        return self._region_counts[team]
    
    def territory(self, team: Team):
        if team == Team.BLUE:
            stack = ["310560"]
        else:
            stack = ["310570"]
        count = 0
        visited = []
        while len(stack) > 0:
            to_visit = stack.pop()
            facility = self._regions[to_visit]
            visited.append(to_visit)
            for region in facility.links:
                if self._regions[region].faction == facility.faction and region not in visited:
                    stack.append(region)
                    count += 1
        return count

    def get_capturable(self, team: Team) -> List[str]:
        to_return = []
        for facility_id in self._regions:
            if facility_id in ["310560", "310570"]:
                # warpgates are not capturable
                continue
            if self._regions[facility_id].faction == team:
                # Cannot capture your own bases
                continue
            for link_id in self._regions[facility_id].links:
                if self._regions[link_id].faction == team:
                    # Have a connected base? Capturable
                    to_return.append(facility_id)
        return to_return

    def get_region(self, facility_id: str) -> Region:
        if facility_id not in self._regions:
            return None
        return self._regions[facility_id]

    def percentages(self) -> MapControl:
        red_bases = 0
        blue_bases = 0
        ns_bases = 0
        for facility_id in self._regions:
            if facility_id in ["310560", "310570"]:
                continue
            if self._regions[facility_id].faction == Team.RED:
                red_bases += 1
            elif self._regions[facility_id].faction == Team.BLUE:
                blue_bases += 1
            elif self._regions[facility_id].faction == Team.NONE:
                ns_bases += 1
        return MapControl(
            0,
            int(100 * blue_bases / (len(self._regions) - 2)),
            int(100 * red_bases / (len(self._regions) - 2)),
            0,
            int(100 * ns_bases / (len(self._regions) - 2))
        )