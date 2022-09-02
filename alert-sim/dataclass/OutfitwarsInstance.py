from auraxium import ps2

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
from typing import Optional
from constants import AlertState, Ps2alertsEventType, World, Zone, Faction
from .MetagameResult import MetagameResult    

@dataclass_json
@dataclass
class Outfit:
    id: int
    name: str
    faction: Faction
    alias: Optional[str]


@dataclass_json
@dataclass
class Teams:
    red: Outfit
    blue: Outfit


@dataclass_json
@dataclass
class OutfitwarsInstance:
    censusInstanceId: int
    zoneInstanceId: str
    world: World
    zone: Zone
    timeStarted: datetime
    phase: int
    round: int
    teams: Teams
    instanceId: str = ''
    timeEnded: Optional[datetime] = None
    result: MetagameResult = MetagameResult(33, 33, 33, 0, 0)
    duration: int = 60 * 90 * 1000 # 90 minutes
    state: AlertState = AlertState.STARTED
    mapVersion: str = '1.0'
    ps2alertsEventType: Ps2alertsEventType = Ps2alertsEventType.OUTFIT_WARS_AUG_2022
    features = {'captureHistory': True, 'xpm': True}

    def __post_init__(self):
        self.instanceId = 'outfitwars-'+str(int(self.world))+'-'+str(int(self.zone))+'-'+self.zoneInstanceId
        self.mapVersion = '1.1' if self.zone == Zone.OSHUR else '1.0'
