from datetime import datetime
from time import sleep
from typing import Dict, List, Optional, Tuple
from threading import Event, Thread
from argparse import ArgumentParser

import asyncio
import auraxium
from auraxium import ps2
import random

from constants import Team, Classes, MetagameEventType, MetagameEventState, Faction, Vehicles, VEHICLE_WEAPONS
from dataclass import OutfitwarsInstance, Outfit, Teams
from events import MetagameEvent, DeathEvent, FacilityControlEvent, VehicleDestroyEvent
from service import get_rabbit, RabbitConnection, RabbitService, Logger
from state import NexusMap

logger = Logger.getLogger("Match")

#BLUE_OUTFIT = 37571208657592881 # [HMRD]
#RED_OUTFIT = 37570391403474491  # [UN17]
MAX_CAPTURES = 20

VS_WEAPON = 80   # Orion
NC_WEAPON = 7169 # GD-7F
TR_WEAPON = 7254 # MSW-R
NSO_WEAPON = 6009899 # XMG-100

weapons = {
    Faction.VS: VS_WEAPON,
    Faction.NC: NC_WEAPON,
    Faction.TR: TR_WEAPON,
    Faction.NSO: NSO_WEAPON
}

tiebreaker_points = { Team.RED: 0, Team.BLUE: 0 }
tbpool = 500

def tiebreaker_worker(interval: float, nexus: NexusMap) -> Tuple[Thread, Event]:
    stop = Event()
    def work():
        global tiebreaker_points, tbpool
        while not stop.wait(interval):
            for team in tiebreaker_points:
                points = nexus.count(team) * 2
                if points > tbpool:
                    points = tbpool
                tiebreaker_points[team] += points
                tbpool -= points
    thread = Thread(target=work)
    return thread, stop


def vehicle_destroy_worker(
        interval: float,
        event: OutfitwarsInstance,
        players: Dict[int, List[int]] = {
            37571208657592881: [5428085259783352737],
            37570391403474491: [5428297992006446465, 5428985062301123025]
        },
        delay: float = 0
    ) -> Tuple[Thread, Event]:
    stop = Event()
    def work():
        global weapons
        sleep(delay)
        vehicle_destroy_queue = f'aggregator-outfitwars-{event.world}-{event.zone}-{event.zoneInstanceId}-VehicleDestroy'
        thread_rabbit = RabbitService(RabbitConnection())
        while not stop.wait(interval):
            attackerOutfitId = random.choice(list(players.keys()))
            victimOutfitId = random.choice(list(players.keys()))
            i = 0
            while attackerOutfitId == victimOutfitId and i < 5: # 0.5^5 == 3.125% tk rate
                victimOutfitId = random.choice(list(players.keys()))
                i += 1
            attackerOutfit = event.teams.red if event.teams.red.id == attackerOutfitId else event.teams.blue
            attacker = random.choice(players[attackerOutfitId])
            attackerVehicle = random.choice([0, *Vehicles.by_faction(attackerOutfit.faction)])
            if attackerVehicle != 0:
                attackerWeapon = VEHICLE_WEAPONS[attackerVehicle][attackerOutfit.faction]
            else:
                attackerWeapon = weapons[attackerOutfit.faction]
            victimOutfit = event.teams.red if event.teams.red.id == victimOutfitId else event.teams.blue
            victim = random.choice(players[victimOutfitId])
            victimVehicle = random.choice(Vehicles.by_faction(victimOutfit.faction))
            vehicleDestroy = VehicleDestroyEvent(
                world_id=str(int(event.world)),
                attacker_character_id=str(attacker),
                attacker_loadout_id=str(int(random.choice(Classes.by_faction(attackerOutfit.faction)))),
                attacker_team_id='2' if attackerOutfitId == event.teams.blue.id else '3',
                attacker_vehicle_id=str(attackerVehicle),
                attacker_weapon_id=str(attackerWeapon),
                character_id=str(victim),
                faction_id=str(int(victimOutfit.faction)),
                team_id='2' if victimOutfitId == event.teams.blue.id else '3',
                vehicle_id=str(victimVehicle),
                zone_id=(int(event.zoneInstanceId) << 16) | int(event.zone),
            )
            thread_rabbit.send(vehicleDestroy, vehicle_destroy_queue)
    thread = Thread(target=work)
    return thread, stop


def death_worker(
        interval: float,
        event: OutfitwarsInstance,
        players: Dict[int, List[int]] = {
            37571208657592881: [5428085259783352737],
            37570391403474491: [5428297992006446465, 5428985062301123025]
        },
        delay: float = 0
    ) -> Tuple[Thread, Event]:
    stop = Event()
    def work():
        global weapons
        sleep(delay)
        death_queue = f'aggregator-outfitwars-{event.world}-{event.zone}-{event.zoneInstanceId}-Death'
        thread_rabbit = RabbitService(RabbitConnection())
        #players = [BLUE_PLAYER, RED_PLAYER, NSO_RED_PLAYER]
        while not stop.wait(interval):
            attackerOutfitId = random.choice(list(players.keys()))
            victimOutfitId = random.choice(list(players.keys()))
            i = 0
            while attackerOutfitId == victimOutfitId and i < 5: # 0.5^5 == 3.125% tk rate
                victimOutfitId = random.choice(list(players.keys()))
                i += 1
            attackerOutfit = event.teams.red if event.teams.red.id == attackerOutfitId else event.teams.blue
            attacker = random.choice(players[attackerOutfitId])
            victimOutfit = event.teams.red if event.teams.red.id == victimOutfitId else event.teams.blue
            victim = random.choice(players[victimOutfitId])
            death = DeathEvent(
                attacker_character_id=str(attacker),
                attacker_loadout_id=str(int(random.choice(Classes.by_faction(attackerOutfit.faction)))),
                attacker_weapon_id=str(weapons[attackerOutfit.faction]),
                attacker_team_id='2' if attackerOutfitId == event.teams.blue.id else '3',
                character_id=str(victim),
                character_loadout_id=str(int(random.choice(Classes.by_faction(victimOutfit.faction)))),
                is_headshot=str(1 if random.random() < 0.25 and attacker != victim else 0),
                team_id='2' if victimOutfitId == event.teams.blue.id else '3',
                world_id=str(event.world),
                zone_id=(int(event.zoneInstanceId) << 16) | int(event.zone)
            )
            thread_rabbit.send(death, death_queue)
    thread = Thread(target=work)
    return thread, stop

def nexus_alert(
    world: int,
    instance: int,
    teams: Teams = Teams(
        Outfit(37570391403474491, name="Un1ty", faction=Faction.TR, alias="UN17"),
        Outfit(37571208657592881, name="Drunk Division", faction=Faction.TR, alias="HMRD")
    ),
    members: Dict[int, List[int]] = {
        37570391403474491: [5428297992006446465, 5428985062301123025],
        37571208657592881: [5428085259783352737]
    },
    capture_rate: int = 5,
    death_rate: float = 0.5,
    first_death_delay: float = 0.0,
    vehicle_destroy_rate: float = 30.0,
    vehicle_destroy_delay: float = 0.0) -> Optional[Tuple[Team, Dict[Team, int]]]:

    metagame_event_queue = f'aggregator-{world}-MetagameEvent'

    zone_id = (instance << 16) | 10
    event = OutfitwarsInstance(
        censusInstanceId=random.randint(1, 123),
        zoneInstanceId=str(instance),
        world=world,
        zone=10,
        timeStarted=datetime.now(),
        phase=random.randint(1, 3),
        round=random.randint(1, 7),
        teams=teams
    )

    participant_count = len(members[event.teams.blue.id]) + len(members[event.teams.red.id])
    faction_blue = int((len(members[event.teams.blue.id]) / participant_count) * 100)
    faction_red = 100 - faction_blue

    metagame_event = MetagameEvent(
        instance_id=str(event.censusInstanceId),
        metagame_event_id=str(int(MetagameEventType.NEXUS_OUTFIT_WAR)),
        metagame_event_state=str(int(MetagameEventState.STARTED)),
        metagame_event_state_name="started",
        world_id=str(int(event.world)),
        zone_id=(int(event.zoneInstanceId) << 16) | event.zone,
        faction_vs='0',
        faction_nc=str(faction_blue),
        faction_tr=str(faction_red),
    )
    rabbit = get_rabbit()
    rabbit.send(metagame_event, metagame_event_queue)
    death_thread, death_stop_event = None, None
    vehicle_destroy_thread, vehicle_destroy_stop_event = None, None
    tb_thread, tb_stop_event = None, None
    nexus = None
    try:
        nexus = NexusMap(zone_id & 0xFFFF)
        to_capture = 0
        captures = MAX_CAPTURES
        fac_control_queue = f'aggregator-outfitwars-{int(event.world)}-{int(event.zone)}-{event.zoneInstanceId}-FacilityControl'
        death_thread, death_stop_event = death_worker(death_rate, event, members, first_death_delay)
        vehicle_destroy_thread, vehicle_destroy_stop_event = vehicle_destroy_worker(vehicle_destroy_rate, event, members, vehicle_destroy_delay)
        tb_thread, tb_stop_event = tiebreaker_worker(60, nexus)
        tb_thread.start()
        death_thread.start()
        vehicle_destroy_thread.start()
        while to_capture not in ['310610', '310600'] and captures > 0:
            sleep(capture_rate)
            team = random.choice([Team.BLUE, Team.RED])
            to_capture = random.choice(nexus.get_capturable(team))
            old_faction = nexus.get_region(to_capture).faction
            nexus.capture(to_capture, team)
            # it appears from the PTS match that outfits might not get credit for captures.
            # Now that we have team id, we can compensate for that on our side ^.^
            if team == Team.BLUE and event.teams.blue.faction == Team.BLUE:
                outfit_id = str(event.teams.blue.id)
            elif team == Team.RED and event.teams.red.faction == Team.RED:
                outfit_id = str(event.teams.red.id)
            else:
                outfit_id = "0"
            facility_control = FacilityControlEvent(
                facility_id=str(to_capture),
                zone_id=str(zone_id),
                world_id=str(int(event.world)),
                old_faction_id=str(int(old_faction)),
                new_faction_id=str(int(team)),
                outfit_id=outfit_id,
            )
            rabbit.send(facility_control, fac_control_queue)
            captures -= 1

        if to_capture in ['310610', '310600']:
            tiebreaker_points[team] += tbpool
            tbpool = 0
    finally:
        metagame_end_event = MetagameEvent(
            instance_id=str(event.censusInstanceId),
            metagame_event_id=str(int(MetagameEventType.NEXUS_OUTFIT_WAR)),
            metagame_event_state=str(int(MetagameEventState.FINISHED)),
            metagame_event_state_name="ended",
            world_id=str(int(event.world)),
            zone_id=(int(event.zoneInstanceId) << 16) | event.zone,
            faction_vs='0',
            faction_nc=str(faction_blue),
            faction_tr=str(faction_red),
        )
        if death_stop_event and death_thread:
            death_stop_event.set()
            if death_thread.is_alive():
                death_thread.join()

        if vehicle_destroy_stop_event and vehicle_destroy_thread:
            vehicle_destroy_stop_event.set()
            if vehicle_destroy_thread.is_alive():
                vehicle_destroy_thread.join()

        if tb_stop_event and tb_thread:
            tb_stop_event.set()
            if tb_thread.is_alive():
                tb_thread.join()

        rabbit.send(metagame_end_event, metagame_event_queue)
        if nexus:
            points = {
                Team.RED: tiebreaker_points[Team.RED],
                Team.BLUE: tiebreaker_points[Team.BLUE]
            }
            winner = Team.RED if nexus.territory(Team.RED) > nexus.territory(Team.BLUE) else Team.BLUE
            return winner, points


async def build_outfit_data(service_id: str, red_outfit_id: int, blue_outfit_id: int):
    if not service_id.startswith("s:"):
        service_id = f"s:{service_id}"
    async with auraxium.Client(service_id=service_id) as client:
        logger.info("Retrieving outfit data...")
        red_outfit, blue_outfit = await asyncio.gather(
            client.get_by_id(ps2.Outfit, red_outfit_id),
            client.get_by_id(ps2.Outfit, blue_outfit_id)
        )
        if red_outfit is None or blue_outfit is None:
            raise ValueError(f"{'Both' if red_outfit is None and blue_outfit is None else ('Red' if red_outfit is None else 'Blue')} outfit(s) do(es) not exist!")

        (red_leader, #standing by
         blue_leader, red_members, blue_members) = await asyncio.gather(
            red_outfit.leader(),
            blue_outfit.leader(),
            red_outfit.members(),
            blue_outfit.members()
        )
        red_leader.character()

        (red_leader_character, blue_leader_character) = await asyncio.gather(
            red_leader.character(),
            blue_leader.character()
        )

        red_outfit_data = Outfit(red_outfit.id, red_outfit.name, red_leader_character.faction_id, red_outfit.alias)
        blue_outfit_data = Outfit(blue_outfit.id, blue_outfit.name, blue_leader_character.faction_id, blue_outfit.alias)
        character_ids = {
            red_outfit.id: [member.id for member in red_members[:48]],
            blue_outfit.id: [member.id for member in blue_members[:48]],
        }

    return Teams(red_outfit_data, blue_outfit_data), character_ids


def start_alert(teams: Teams, members: Dict[int, List], world: int, instance: int, capture_rate: int, death_rate: float, death_delay: float, vehicle_destroy_rate: float, vehicle_destroy_delay: float):

    logger.info(f"Starting alert on world {world}, zone instance {instance}")
    result = nexus_alert(world, instance, teams, members, capture_rate, death_rate, death_delay, vehicle_destroy_rate, vehicle_destroy_delay)
    logger.info(f"Finished alert on world {world}, zone instance {instance}")
    if result is not None:
        logger.info(f"Winner was team {result[0].name.capitalize()}")
    return instance, result

# Simulator that fakes an alert on Nexus with a bunch of random (possible) captures
#   Basically intended to test out various scenarios that could happen with outfit wars
def main():
    global logger
    parser = ArgumentParser(description="A tool that can fake a single outfit wars match between two outfits")
    parser.add_argument("service_id", type=str, help="The PS2 Census service id used for querying outfit (member) data")
    parser.add_argument("--red-outfit-id", "-r", type=int, default=37570391403474491, help="The outfit id for the red team")
    parser.add_argument("--blue-outfit-id", "-b", type=int, default=37571208657592881, help="The outfit id for the blue team")
    parser.add_argument("--world", "-w", type=int, choices=[1, 10, 13, 17], default=1, help="The world having the outfit war")
    parser.add_argument("--capture-rate", "-c", type=int, default=5, help="The number of seconds between base captures")
    parser.add_argument("--death-rate", "-d", type=float, default=1.0, help="The number of seconds between deaths (can be a decimal)")
    parser.add_argument("--death-delay", "-l", type=float, default=0.0, help="The decimal number of seconds to delay the first death by")
    args = parser.parse_args()

    try:
        teams, members = asyncio.get_event_loop().run_until_complete(build_outfit_data(args.service_id, args.red_outfit_id, args.blue_outfit_id))
    except ValueError as e:
        logger.error(str(e))
        exit(1)

    start_alert(teams, members, args.world, random.randint(0, 0xFFFF), args.capture_rate, args.death_rate, args.death_delay)


if __name__ == "__main__":
    main()
