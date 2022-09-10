from dataclasses import dataclass
from typing import Dict


@dataclass
class VehicleDestroyReplayEvent:
    character_id: str
    vehicle_definition_id: str
    faction_id: str
    attacker_player_guid: str
    attacker_character_id: str
    attacker_loadout_id: str
    attacker_weapon_id: str
    attacker_vehicle_id: str
    projectile_id: str
    timestamp: str
    zone_id: str
    world_id: str
    attacker_team_id: str
    team_id: str
    event_type: str = "VehicleDestroy"
    table_type: str = "vehicle_destroy"

    @classmethod
    def from_json(cls, data: Dict) -> 'VehicleDestroyReplayEvent':
        character_id = data["character_id"]
        vehicle_definition_id = data["vehicle_definition_id"]
        faction_id = data["faction_id"]
        attacker_player_guid = data["attacker_player_guid"]
        attacker_character_id = data["attacker_character_id"]
        attacker_loadout_id = data["attacker_loadout_id"]
        attacker_weapon_id = data["attacker_weapon_id"]
        attacker_vehicle_id = data["attacker_vehicle_id"]
        projectile_id = data["projectile_id"]
        timestamp = data["timestamp"]
        zone_id = data["zone_id"]
        world_id = data["world_id"]
        attacker_team_id = data["attacker_team_id"]
        team_id = data["team_id"]
        return cls(
            character_id,
            vehicle_definition_id,
            faction_id,
            attacker_player_guid,
            attacker_character_id,
            attacker_loadout_id,
            attacker_weapon_id,
            attacker_vehicle_id,
            projectile_id,
            timestamp,
            zone_id,
            world_id,
            attacker_team_id,
            team_id,
        )