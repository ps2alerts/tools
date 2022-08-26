from dataclasses import asdict
from datetime import datetime
import random
from time import sleep

from constants import Loadout, World, Zone
from dataclass import TerritoryInstance
from events import DeathEvent
from operations import DeathEventOps, MetagameEventOps, PreflightChecksOps, Ps2AlertsApiOps
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

    # Generate some deaths (WIP)
#     deathEvents = generateDeaths(instance)
#     DeathEventOps.send(instance, deathEvents, channel)

    # Validate the deaths have gone in correctly using the cases


    # Create facility controls
    # Validate the facility controls have adjusted the result as expectedß

    MetagameEventOps.endTerritoryInstance(instance, channel)
    log.info('Finished!')

def generateDeaths(instance: TerritoryInstance):
    cases = [
        {
            attacker: 5428010618035323201, # [DIG] Maelstrome26
            attackerLoadout: Loadout.HEAVY_VS
            victim: 5428662532300209473, # [D1GT] MaelstromeDakkaside
            victimLoadout: Loadout.HEAVY_TR
            weapon: 7540 # Lasher
            headshot: 0
        },
        {
            attacker: 5428010618035323201, # [DIG] Maelstrome26
            attackerLoadout: Loadout.HEAVY_VS
            victim: 5428010618036469857, # [CTIA] DrZerg
            victimLoadout: Loadout.INFIL_TR
            weapon: 7540 # Lasher
            headshot: 0
        },
        {
            attacker: 5428010618036469857, # [CTIA] DrZerg
            attackerLoadout: Loadout.INFIL_TR
            victim: 5428026242699274033, # [DIGT] Heregas
            victimLoadout: Loadout.HEAVY_VS
            weapon: 7170 # AC-X11
            headshot: 1
        }
    ]

    # For each case, create event and publish it

if __name__ == "__main__":
    main()
