from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class MapControl:
    vs: float
    nc: float
    tr: float
    cutoff: float
    outOfPlay: float
