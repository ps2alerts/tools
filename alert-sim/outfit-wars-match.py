from dataclasses import dataclass
from datetime import datetime, timezone
from enum import IntEnum
import json
from time import sleep
from typing import List, Optional, Tuple

import pika
from pika.exceptions import UnroutableError
from pika.adapters.blocking_connection import BlockingChannel
from pika.credentials import PlainCredentials
from pika import frame
from pika import spec
import random
import requests

from threading import Event, Thread

INIT_BLUE_REGIONS = [310560, 310610, 310550, 310520]
INIT_RED_REGIONS  = [310570, 310600, 310540, 310510]
INIT_NS_REGIONS   = [310530, 310500, 310590]
BLUE_OUTFIT = 37571208657592881 # [HMRD]
RED_OUTFIT = 37570391403474491
MAX_CAPTURES = 20

BLUE_PLAYER = 5428085259783352737    # [HMRD] Fyreflyz
NC_WEAPON = 7169 # GD-7F
RED_PLAYER = 5428297992006446465     # RiderAnton
TR_WEAPON = 7254 # MSW-R
NSO_RED_PLAYER = 5428985062301123025 # RobotAnton
NSO_WEAPON = 6013842 # dunno name but its something nso killed with

class Map:
    def __init__(self, zone_id: int, version: str = "1.0"):
        response = requests.get(str(BASE / "census" / "regions" / str(zone_id) / version), verify=False)
        assert 200 <= response.status_code <= 299, "Failed to retrieve map data"
        data = response.json()
        self._regions = {}
        for region in data["map_region_list"]:
            self._regions[region["facility_id"]] = {
                "name": region["facility_name"],
                "links": [link["facility_id_b"] for link in region["facility_links"]],
                "faction": (Team.BLUE if int(region["facility_id"]) in INIT_BLUE_REGIONS
                       else Team.RED  if int(region["facility_id"]) in INIT_RED_REGIONS
                       else Team.NONE)
            }

        for facility_id in self._regions:
            for link_id in self._regions[facility_id]["links"]:
                if facility_id not in self._regions[link_id]["links"]:
                    self._regions[link_id]["links"].append(facility_id)

    def capture(self, facility_id: int, team: Team):
        self._regions[str(facility_id)]["faction"] = team

    def get_capturable(self, team: Team) -> List[int]:
        to_return = []
        for facility_id in self._regions:
            if facility_id in ["310560", "310570"]:
                # warpgates are not capturable
                continue
            if self._regions[facility_id]["faction"] == team:
                # Cannot capture your own bases
                continue
            for link_id in self._regions[facility_id]["links"]:
                if self._regions[link_id]["faction"] == team:
                    # Have a connected base? Capturable
                    to_return.append(int(facility_id))
        return to_return

    def get_region(self, facility_id: int):
        if str(facility_id) not in self._regions:
            return None
        return self._regions[str(facility_id)]

    def percentages(self) -> MapControl:
        red_bases = 0
        blue_bases = 0
        ns_bases = 0
        for facility_id in self._regions:
            if facility_id in ["310560", "310570"]:
                continue
            if self._regions[facility_id]["faction"] == Team.RED:
                red_bases += 1
            elif self._regions[facility_id]["faction"] == Team.BLUE:
                blue_bases += 1
            elif self._regions[facility_id]["faction"] == Team.NONE:
                ns_bases += 1
        return MapControl(
            0,
            int(100 * blue_bases / (len(self._regions) - 2)),
            int(100 * red_bases / (len(self._regions) - 2)),
            0,
            int(100 * ns_bases / (len(self._regions) - 2))
        )

def send_death_event(channel: BlockingChannel, event: MetagameEvent, zone_id: int, attacker: int, attacker_class: Loadout, attacker_weapon: int, victim: int, victim_class: Loadout):
    rabbit_death = RabbitEvent("Death", {
		"event_name": "Death",
        "attacker_character_id": str(attacker),
		"attacker_fire_mode_id": "7404", # This should be different for different weapons but i don't think it matters
		"attacker_loadout_id": str(int(attacker_class)),
		"attacker_vehicle_id": "0", # infants only
		"attacker_weapon_id": str(attacker_weapon),
		"character_id": str(victim),
		"character_loadout_id": str(int(victim_class)),
		"is_critical": "0",
		"is_headshot": "1", # everyones a pro player right?
		"timestamp": str(int(datetime.now().timestamp())),
		"vehicle_id": "0", # this is borked so nobody dies in a vehicle ever according to census
		"world_id": str(event.world),
		"zone_id": str(zone_id)
    }, event.world)
    print("Publishing death event:")
    print(json.dumps(rabbit_death.to_json()))
    channel.basic_publish(
        exchange='',
        routing_key=f'aggregator-outfitwars-{event.world}-{event.zone}-{event.zone_instance}-Death',
        body=json.dumps(rabbit_death.to_json()),
        properties=pika.BasicProperties(
            content_type='text/plain',
            delivery_mode=1
        )
    )

def send_facility_control(channel: BlockingChannel, event: MetagameEvent, zone_id: int, facility_id: int, old: Team, new: Team, outfit_id: int):
    ret: frame.Method = channel.queue_declare(queue=f'aggregator-outfitwars-{event.world}-{event.zone}-{event.zone_instance}-FacilityControl', passive=True)
    if type(ret.method) != spec.Queue.DeclareOk:
        print("Queue does not exist?")
        print(ret)
        return
    rabbit_capture = RabbitEvent("FacilityControl", {
        "event_name": "FacilityControl",
        "duration_held": "0",
        "timestamp": str(int(datetime.now().timestamp())),
        "world_id": str(event.world),
        "zone_id": str(zone_id),
        "old_faction_id": str(int(old)),
        "outfit_id": str(outfit_id),
        "new_faction_id": str(int(new)),
        "facility_id": str(facility_id),
    }, event.world)
    print("Publishing facility control event:")
    print(json.dumps(rabbit_capture.to_json()))
    channel.basic_publish(
        exchange='',
        routing_key=f'aggregator-outfitwars-{event.world}-{event.zone}-{event.zone_instance}-FacilityControl',
        body=json.dumps(rabbit_capture.to_json()),
        properties=pika.BasicProperties(
            content_type='text/plain',
            delivery_mode=1
        )
    )

def death_worker(interval: float, event: MetagameEvent) -> Tuple[Thread, Event]:
    stop = Event()
    def work():
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                credentials=PlainCredentials('guest', 'guest')
            )
        )
        channel = connection.channel()
        players = [BLUE_PLAYER, RED_PLAYER, NSO_RED_PLAYER]
        weapons = {
            BLUE_PLAYER: NC_WEAPON,
            RED_PLAYER: TR_WEAPON,
            NSO_RED_PLAYER: NSO_WEAPON
        }
        classes = {
            BLUE_PLAYER: NC_CLASSES,
            RED_PLAYER: TR_CLASSES,
            NSO_RED_PLAYER: NSO_CLASSES
        }
        while not stop.wait(interval):
            attacker = random.choice(players)
            attacker_weapon = weapons[attacker]
            attacker_class = random.choice(classes[attacker])
            victim = random.choice(players)
            victim_class = random.choice(classes[victim])
            send_death_event(
                channel,
                event,
                (event.zone_instance << 16) | event.zone,
                attacker,
                attacker_class,
                attacker_weapon,
                victim,
                victim_class
            )
    thread = Thread(target=work)
    return thread, stop

def nexus_alert(world: int, instance: int):

    queueName = f'aggregator-{world}-MetagameEvent'
    ret: frame.Method = channel.queue_declare(queue=queueName, passive=True)
    if type(ret.method) != spec.Queue.DeclareOk:
        print("Queue does not exist?")
        print(ret)
        return

    zone_id = (instance << 16) | 10
    event = MetagameEvent(world, 10, instance, random.randint(1, 123), datetime.utcnow().replace(tzinfo=timezone.utc))
#     rabbit_metagame = RabbitEvent("AdminMessage", {
#         "action": "start",
#         "body": {
#             "duration": str(int(event.duration)),
#             "faction": "0",
#             "instanceId": event.instance_id(),
#             "metagameType": "outfitwars",
#             "start": str(int(event.time_started.timestamp())),
#             "world": str(event.world),
#             "zone": str(zone_id)
#         }
#     }, event.world)
    rabbit_metagame = RabbitEvent("MetagameEvent",
        {
            "event_name": "MetagameEvent",
            "experience_bonus": "",
            "faction_vs": "0",
            "faction_nc": "50",
            "faction_tr": "50",
            "instance_id": str(event.census_id),
            "metagame_event_id": str(event._type),
            "metagame_event_state": "137",
            "metagame_event_state_name": "started",
            "timestamp": str(int(datetime.now().timestamp())),
            "world_id": str(event.world),
            "zone_id": str(zone_id),
        },
        event.world
    )
    print("Publishing metagame event:")
    print(json.dumps(rabbit_metagame.to_json()))
    try:
        channel.basic_publish(
            exchange='',
            routing_key=queueName,
            body=json.dumps(rabbit_metagame.to_json()),
            properties=pika.BasicProperties(
                content_type='text/plain',
                delivery_mode=1
            ),
            mandatory=True
        )
    except UnroutableError as e:
        print(e.messages[0].body)
        print(e.messages[0].method)
        print(e.messages[0].properties)
        return 1
    try:
        nexus = Map(zone_id & 0xFFFF)
        death_thread, death_stop_event = death_worker(1.0, event)
        to_capture = 0
        captures = MAX_CAPTURES
        death_thread.start()
        while to_capture not in [310610, 310600] and captures > 0:
            sleep(5)
            team = random.choice([Team.BLUE, Team.RED])
            to_capture = random.choice(nexus.get_capturable(team))
            old_faction = nexus.get_region(to_capture)["faction"]
            nexus.capture(to_capture, team)
            send_facility_control(channel, event, zone_id, to_capture, old_faction, team, RED_OUTFIT if team == Team.RED else BLUE_OUTFIT)

            captures -= 1

    finally:
        death_stop_event.set()
        rabbit_end = RabbitEvent("AdminMessage", {
            "action": "end",
            "body": {
                "instanceId": event.instance_id(),
            }
        }, event.world)
        print("Publishing metagame end event:")
        print(json.dumps(rabbit_end.to_json()))
        channel.basic_publish(
            exchange='',
            routing_key='aggregator-admin-development-ps2',
            body=json.dumps(rabbit_end.to_json()),
            properties=pika.BasicProperties(
                content_type='text/plain',
                delivery_mode=1
            )
        )
        death_thread.join()

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
