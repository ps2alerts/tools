import sys
sys.path.append("..") # Adds higher directory to python modules path. This is so dumb.

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
from typing import Optional
from constants import AlertState, Ps2alertsEventType, World, Zone
from .MetagameResult import MetagameResult

@dataclass_json
@dataclass
class TerritoryInstance:
    censusInstanceId: int
    world: World
    zone: Zone
    timeStarted: int
    instanceId: str = ''
    timeEnded: Optional[datetime] = None
    result: MetagameResult = MetagameResult(33, 33, 33, 0, 0)
    duration: int = 60 * 90 * 1000 # 90 minutes
    state: AlertState = AlertState.STARTED
    mapVersion: str = '1.0'
    ps2alertsEventType: Ps2alertsEventType = Ps2alertsEventType.LIVE_METAGAME

    def __post_init__(self):
        self.instanceId = str(self.world.value)+'-'+str(self.censusInstanceId)
        self.mapVersion = '1.1' if self.zone == Zone.OSHUR else '1.0'
