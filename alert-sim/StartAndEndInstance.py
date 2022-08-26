from dataclasses import asdict
from datetime import datetime
import random
from time import sleep

from constants import Loadout, World, Zone
from dataclass import TerritoryInstance
from events import DeathEvent
from operations import MetagameEventOps, PreflightChecksOps, Ps2AlertsApiOps
from service import Logger, RabbitConnection
log = Logger.getLogger()

def main():
    log.info('Starting scenario...')
    PreflightChecksOps.run()

    channel = RabbitConnection.getChannel()

    instance = TerritoryInstance(
        censusInstanceId=random.randint(123, 99999),
        world=World.MILLER,
        zone=Zone.INDAR,
        timeStarted=datetime.now().isoformat()
    )

    MetagameEventOps.startTerritoryInstance(instance, channel)
    MetagameEventOps.endTerritoryInstance(instance, channel)
    log.info('Finished!')

if __name__ == "__main__":
    main()
