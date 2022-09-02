from dataclasses import dataclass
from dataclasses_json import dataclass_json

from .StreamEvent import StreamEvent

@dataclass_json
@dataclass
class VehicleDestroyEvent(StreamEvent):
    event_name: str = 'VehicleDestroy'
    world_id: str = '10' # Miller
    attacker_character_id: str = '5428010618035323201' # Maelstrome26
    attacker_loadout_id: str = '20' # VS Heavy Assault
    attacker_vehicle_id: str = '0'
    attacker_weapon_id: str = '7540' # Lasher
    attacker_team_id: str = '1' # Very pog
    facility_id: str = '0'
    character_id: str = '5428662532300209473' # MaelstromeDakkaside
    character_loadout_id: str = '13' # TR Heavy Assault
    faction_id: str = '3'
    team_id: str = '3' # Very pog indeed
    timestamp: str = '' # post_init will set this to the current timestamp if not set
    vehicle_id: str = '0' # Dead value, never emitted by Census
    zone_id: str = '2' # Indar
