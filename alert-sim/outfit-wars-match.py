from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
from time import sleep
from typing import List, Tuple
from threading import Event, Thread

import random

from constants import Team, Classes, MetagameEventType, MetagameEventState
from dataclass import OutfitwarsInstance
from events import MetagameEvent, DeathEvent, FacilityControlEvent
from service import rabbit, RabbitConnection, RabbitService
from state import NexusMap


BLUE_OUTFIT = 37571208657592881 # [HMRD]
RED_OUTFIT = 37570391403474491  # [UN17]
MAX_CAPTURES = 20

BLUE_PLAYER = 5428085259783352737    # [HMRD] Fyreflyz
NC_WEAPON = 7169 # GD-7F
RED_PLAYER = 5428297992006446465     # RiderAnton
TR_WEAPON = 7254 # MSW-R
NSO_RED_PLAYER = 5428985062301123025 # RobotAnton
NSO_WEAPON = 6013842 # dunno name but its something nso killed with


def death_worker(interval: float, event: OutfitwarsInstance) -> Tuple[Thread, Event]:
    stop = Event()
    def work():
        death_queue = f'aggregator-outfitwars-{event.world}-{event.zone}-{event.zoneInstanceId}-Death'
        thread_rabbit = RabbitService(RabbitConnection())
        players = [BLUE_PLAYER, RED_PLAYER, NSO_RED_PLAYER]
        weapons = {
            BLUE_PLAYER: NC_WEAPON,
            RED_PLAYER: TR_WEAPON,
            NSO_RED_PLAYER: NSO_WEAPON
        }
        classes = {
            BLUE_PLAYER: Classes.NC_CLASSES,
            RED_PLAYER: Classes.TR_CLASSES,
            NSO_RED_PLAYER: Classes.NSO_CLASSES
        }
        while not stop.wait(interval):
            attacker = random.choice(players)
            victim = random.choice(players)
            death = DeathEvent(
                attacker_character_id=str(attacker), 
                attacker_loadout_id=str(int(random.choice(classes[attacker]))), 
                attacker_weapon_id=str(weapons[attacker]),
                character_id=str(victim),
                character_loadout_id=str(int(random.choice(classes[victim]))),
                world_id=str(event.world),
                zone_id=str((int(event.zoneInstanceId) << 16) | int(event.zone))
            )
            thread_rabbit.send(death, death_queue)
    thread = Thread(target=work)
    return thread, stop

def nexus_alert(world: int, instance: int):
    metagame_event_queue = f'aggregator-{world}-MetagameEvent'

    zone_id = (instance << 16) | 10
    event = OutfitwarsInstance(
        censusInstanceId=random.randint(1, 123),
        zoneInstanceId=instance,
        world=world,
        zone=10,
        timeStarted=datetime.now(),
        phase=random.randint(1, 3),
        round=random.randint(1, 7)
    )

    metagame_event = MetagameEvent(
        instance_id=str(event.censusInstanceId), 
        metagame_event_id=str(int(MetagameEventType.NEXUS_OUTFIT_WAR)), 
        metagame_event_state=str(int(MetagameEventState.STARTED)), 
        metagame_event_state_name="started",
        world_id=str(int(event.world)),
        zone_id=(int(event.zoneInstanceId) << 16) | event.zone,
        faction_vs='0',
        faction_nc='50',
        faction_tr='50'
    )
    rabbit.send(metagame_event, metagame_event_queue)
    try:
        nexus = NexusMap(zone_id & 0xFFFF)
        death_thread, death_stop_event = death_worker(1.0, event)
        to_capture = 0
        captures = MAX_CAPTURES
        fac_control_queue = f'aggregator-outfitwars-{event.world.value}-{event.zone.value}-{event.zoneInstanceId}-FacilityControl'
        death_thread.start()
        while to_capture not in [310610, 310600] and captures > 0:
            sleep(5)
            team = random.choice([Team.BLUE, Team.RED])
            to_capture = random.choice(nexus.get_capturable(team))
            old_faction = nexus.get_region(to_capture).faction
            nexus.capture(to_capture, team)
            outfit_id = str(RED_OUTFIT if team == Team.RED else BLUE_OUTFIT)
            facility_control = FacilityControlEvent(
                facility_id=str(to_capture),
                zone_id=str(zone_id),
                world_id=str(int(event.world)),
                old_faction_id=str(int(old_faction)),
                new_faction_id=str(int(team)),
                outfit_id=outfit_id
            )
            rabbit.send(facility_control, fac_control_queue)
            captures -= 1

    finally:
        metagame_end_event = MetagameEvent(
            instance_id=str(event.censusInstanceId), 
            metagame_event_id=str(int(MetagameEventType.NEXUS_OUTFIT_WAR)), 
            metagame_event_state=str(int(MetagameEventState.FINISHED)), 
            metagame_event_state_name="ended",
            world_id=str(int(event.world)),
            zone_id=(int(event.zoneInstanceId) << 16) | event.zone,
            faction_vs='0',
            faction_nc='50',
            faction_tr='50'
        )
        death_stop_event.set()
        death_thread.join()
        rabbit.send(metagame_end_event, metagame_event_queue)

# Simple simulator that fakes an alert on Nexus with a bunch of random (possible) captures
#   Basically intended to test out various scenarios that could happen with outfit wars
def main():
    world = 1
    instance = random.randint(0, 0xFFFF)
    print(f"Starting alert on world {world}, zone instance {instance}")
    nexus_alert(world, instance)
    print(f"Finished alert on world {world}, zone instance {instance}")

if __name__ == "__main__":
    main()
