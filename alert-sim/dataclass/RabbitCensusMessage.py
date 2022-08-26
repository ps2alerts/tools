from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class RabbitCensusMessage:
    eventName: str
    payload: dict
    worldId: str = '10'
