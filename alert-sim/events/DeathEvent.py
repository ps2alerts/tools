from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime, timezone

@dataclass_json
@dataclass
class DeathEvent:
    event_name = 'Death'
    attacker_character_id: str = '5428010618035323201' # Maelstrome26
    attacker_fire_mode_id: str = '8048' # No idea what this should be
    attacker_loadout_id: str = '20' # VS Heavy Assault
    attacker_vehicle_id: str = '0'
    attacker_weapon_id: str = '7540' # Lasher
    character_id: str = '5428662532300209473' # MaelstromeDakkaside
    character_loadout_id: str = '13' # TR Heavy Assault
    is_critical: str = '0' # Is this even used?
    is_headshot: str = '1' # Cos I have totally the best aim
    timestamp: str = datetime.now().timestamp()
    vehicle_id: str = '0' # Dead value, never emitted by Census
    world_id: str = '10' # Miller
    zone_id: str = '2' # Indar
