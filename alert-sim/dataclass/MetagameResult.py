import sys
sys.path.append("..") # Adds higher directory to python modules path. This is so dumb.

from dataclasses import dataclass
from typing import Optional
from constants import Team

@dataclass
class MetagameResult:
    vs: float
    nc: float
    tr: float
    cutoff: float
    outOfPlay: float
    victor: Optional[Team] = None
    draw: bool = False
    perBasePercentage: float = 100/9
