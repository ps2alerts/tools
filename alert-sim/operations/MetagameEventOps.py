import sys
sys.path.append("..") # Adds higher directory to python modules path. This is so dumb.

from pika.adapters.blocking_connection import BlockingChannel
from constants import MetagameEventType, MetagameEventState
from dataclass import TerritoryInstance
from events import MetagameEvent
from service import RabbitConnection

class MetagameEventOps:
    def startTerritoryInstance(instance: TerritoryInstance, channel: BlockingChannel):
        print('Starting Territory instance')
        queueName = f'aggregator-{instance.world}-MetagameEvent'
        RabbitConnection.declareQueue(queueName, channel)

        metagameEvent = MetagameEvent(
            instance.instanceId,
            str(MetagameEventType.INDAR_ENLIGHTENMENT.value),
            str(MetagameEventState.STARTED.value),
            'started',
            str(instance.world.value),
            str(instance.zone.value),
        )

        print(metagameEvent.to_json())

#         RabbitConnection.publishMessage(
#             queueName,
#             channel,
#             metagameEvent
#         )
