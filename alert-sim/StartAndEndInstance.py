import random
from datetime import datetime
from dataclasses import asdict
from time import sleep

from constants import Loadout, World, Zone
from dataclass import TerritoryInstance
from events import DeathEvent
from operations import MetagameEventOps, PreflightChecksOps, Ps2AlertsApiOps
from service import RabbitConnection

def main():
    PreflightChecksOps.run()

    channel = RabbitConnection.getChannel()

    MetagameEventOps.startTerritoryInstance(instance, channel)
    print('Waiting 10s...')
    sleep(10)
    MetagameEventOps.endTerritoryInstance(instance, channel)
    print('Finished!')

if __name__ == "__main__":
    main()
