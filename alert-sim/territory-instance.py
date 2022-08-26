import random
from datetime import datetime
from dataclasses import asdict
from constants import Loadout, World, Zone
from dataclass import TerritoryInstance
from events import DeathEvent
from operations import MetagameEventOps
from service import RabbitConnection

def main():
    instance = TerritoryInstance(
        censusInstanceId=random.randint(123, 99999),
        world=World.MILLER,
        zone=Zone.INDAR,
        timeStarted=datetime.now().isoformat()
    )

    channel = RabbitConnection.getChannel()

    MetagameEventOps.startTerritoryInstance(instance, channel)

if __name__ == "__main__":
    main()
