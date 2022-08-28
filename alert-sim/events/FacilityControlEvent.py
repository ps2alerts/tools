from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime

from .StreamEvent import StreamEvent

@dataclass_json
@dataclass
class FacilityControlEvent(StreamEvent):
    facility_id: str
    zone_id: str
    timestamp: str = ''  # post_init will set this to the current timestamp if not set
    world_id: str = "10" # Miller
    event_name: str = 'FacilityControl'
    duration_held: str = "0"
    old_faction_id: str = "2" # NC
    new_faction_id: str = "3" # TR
    outfit_id: str = "0"
