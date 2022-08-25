from dataclasses import dataclass

@dataclass
class RabbitCensusMessage:
    eventName: str
    payload: dict
    worldId: str = '10'
