from datetime import datetime
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from .StreamEvent import StreamEvent

@dataclass_json
@dataclass
class MetagameEvent(StreamEvent):
    instance_id: str
    metagame_event_id: str
    metagame_event_state: str
    metagame_event_state_name: str
    world_id: str
    zone_id: str
    timestamp: str = str(int(datetime.now().timestamp()))
    event_name: str = 'MetagameEvent'
    experience_bonus: str = '0'
    faction_vs: str = '33'
    faction_nc: str = '33'
    faction_tr: str = '33'
