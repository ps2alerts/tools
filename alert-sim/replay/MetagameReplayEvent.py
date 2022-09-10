
from dataclasses import dataclass
from typing import Dict


@dataclass
class MetagameReplayEvent:
    metagame_event_id: str
    metagame_event_state: str
    metagame_event_state_name: str
    faction_nc: str
    faction_tr: str
    faction_vs: str
    experience_bonus: str
    timestamp: str
    zone_id: str
    world_id: str
    instance_id: str
    event_type: str = "MetagameEvent"
    table_type: str = "metagame_event"

    @classmethod
    def from_json(cls, data: Dict) -> 'MetagameReplayEvent':
        metagame_event_id = data["metagame_event_id"]
        metagame_event_state = data["metagame_event_state"]
        faction_nc = data["faction_nc"]
        faction_tr = data["faction_tr"]
        faction_vs = data["faction_vs"]
        experience_bonus = data["experience_bonus"]
        timestamp = data["timestamp"]
        zone_id = data["zone_id"]
        world_id = data["world_id"]
        instance_id = data["instance_id"]
        metagame_event_state_name = data["metagame_event_state_name"]
        return cls(
            metagame_event_id,
            metagame_event_state,
            metagame_event_state_name,
            faction_nc,
            faction_tr,
            faction_vs,
            experience_bonus,
            timestamp,
            zone_id,
            world_id,
            instance_id
        )
