from dataclasses import dataclass
from dataclasses_json import dataclass_json

from events import StreamEvent

@dataclass_json
@dataclass
class RabbitCensusMessage:
    eventName: str
    worldId: str
    payload: StreamEvent
