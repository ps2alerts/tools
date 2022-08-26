from dataclasses import dataclass
from dataclasses_json import dataclass_json

from typing import List
from constants import Team

@dataclass_json
@dataclass
class Region:
    name: str
    links: List[str]
    faction: Team