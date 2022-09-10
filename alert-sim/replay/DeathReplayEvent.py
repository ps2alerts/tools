from dataclasses import dataclass
from typing import Dict, Literal, Union


@dataclass
class DeathReplayEvent:
    character_id: str
    attacker_character_id: str
    is_headshot: str
    is_critical: str
    attacker_weapon_id: str
    attacker_vehicle_id: str
    timestamp: str
    zone_id: str
    world_id: str
    character_loadout_id: str
    attacker_loadout_id: str
    attacker_team_id: str
    team_id: str
    event_type: Literal["Death"] = "Death"
    table_type: Union[Literal["deaths"], Literal["kills"]] = "deaths"

    @classmethod
    def from_json(cls, data: Dict) -> 'DeathReplayEvent':
        character_id = data["character_id"]
        attacker_character_id = data["attacker_character_id"]
        is_headshot = data["is_headshot"]
        is_critical = data["is_critical"]
        attacker_weapon_id = data["attacker_weapon_id"]
        attacker_vehicle_id = data["attacker_vehicle_id"]
        timestamp = data["timestamp"]
        zone_id = data["zone_id"]
        world_id = data["world_id"]
        character_loadout_id = data["character_loadout_id"]
        attacker_loadout_id = data["attacker_loadout_id"]
        attacker_team_id = data["attacker_team_id"]
        team_id = data["team_id"]
        return cls(
            character_id,
            attacker_character_id,
            is_headshot,
            is_critical,
            attacker_weapon_id,
            attacker_vehicle_id,
            timestamp,
            zone_id,
            world_id,
            character_loadout_id,
            attacker_loadout_id,
            attacker_team_id,
            team_id
        )