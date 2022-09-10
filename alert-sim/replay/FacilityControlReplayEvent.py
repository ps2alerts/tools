
from dataclasses import dataclass
from typing import Dict


@dataclass
class FacilityControlReplayEvent:
    facility_id: str
    faction_old: str
    faction_new: str
    duration_held: str
    objective_id: str
    timestamp: str
    zone_id: str
    world_id: str
    outfit_id: str
    event_type: str = "FacilityControl"
    table_type: str = "facility_event"

    @classmethod
    def from_json(cls, data: Dict) -> 'FacilityControlReplayEvent':
        facility_id = data["facility_id"]
        faction_old = data["faction_old"]
        faction_new = data["faction_new"]
        duration_held = data["duration_held"]
        objective_id = data["objective_id"]
        timestamp = data["timestamp"]
        zone_id = data["zone_id"]
        world_id = data["world_id"]
        outfit_id = data["outfit_id"]
        return cls(
            facility_id,
            faction_old,
            faction_new,
            duration_held,
            objective_id,
            timestamp,
            zone_id,
            world_id,
            outfit_id
        )