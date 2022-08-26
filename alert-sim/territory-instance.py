import random
from datetime import datetime, timezone
from dataclasses import asdict
from constants import Loadout, World, Zone
from dataclass import TerritoryInstance
from events import DeathEvent
from operations import MetagameEventOps
from service import RabbitConnection

# def send_death_event(
#     channel: BlockingChannel,
#     event: MetagameEvent,
#     zone_id: int,
#     attacker: int,
#     attacker_class: Loadout,
#     attacker_weapon: int,
#     victim: int,
#     victim_class: Loadout
# ):
#     deathEvent = DeathEvent(
#         attacker_character_id=str(attacker),
#         character_id=str(victim)
#         world_id=str(world_id)
#         zone_id=str(zone_id)
#     )
#     rabbit_death = RabbitEvent("Death", asdict(deathEvent), event.world)
#     print("Publishing death event:")
#     print(json.dumps(asdict(rabbit_death))
#     channel.basic_publish(
#         exchange='',
#         routing_key=f'aggregator-outfitwars-{event.world}-{event.zone}-{event.zone_instance}-Death',
#         body=json.dumps(rabbit_death.to_json()),
#         properties=pika.BasicProperties(
#             content_type='text/plain',
#             delivery_mode=1
#         )
#     )

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
