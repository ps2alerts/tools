from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime

from .StreamEvent import StreamEvent

@dataclass_json
@dataclass
class DeathEvent(StreamEvent):
    event_name: str = 'Death'
    world_id: str = '10' # Miller
    attacker_character_id: str = '5428010618035323201' # Maelstrome26
    attacker_fire_mode_id: str = '8048' # No idea what this should be
    attacker_loadout_id: str = '20' # VS Heavy Assault
    attacker_vehicle_id: str = '0'
    attacker_weapon_id: str = '7540' # Lasher
    attacker_team_id: str = '1' # Very pog
    character_id: str = '5428662532300209473' # MaelstromeDakkaside
    character_loadout_id: str = '13' # TR Heavy Assault
    is_critical: str = '0' # Is this even used?
    is_headshot: str = '1' # Cos I have totally the best aim
    team_id: str = '3' # Very pog indeed
    timestamp: str = '' # post_init will set this to the current timestamp if not set
    vehicle_id: str = '0' # Dead value, never emitted by Census
    zone_id: str = '2' # Indar
