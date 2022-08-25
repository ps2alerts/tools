from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from constants import Faction
from .MapControl import MapControl

@dataclass
class FacilityControl:
    instance: str
    facilityId: int
    timestamp: datetime
    oldFaction: Faction
    newFaction: Faction
    duration_held: int = 0
    isInitial: bool = False
    isDefence: bool = False
    outfitCaptured: Optional[int] = None
    mapControl: Optional[MapControl] = None

    def __post_init__(self):
        self.timestamp = self.timestamp.isoformat()
        asdict(self.control) if self.mapControl is not None else None
