import sys
sys.path.append("..") # Adds higher directory to python modules path. This is so dumb.

from pika.adapters.blocking_connection import BlockingChannel
from dataclasses import asdict
from datetime import datetime
from constants import MetagameEventType, MetagameEventState
from dataclass import RabbitCensusMessage, TerritoryInstance
from events import MetagameEvent
from service import RabbitConnection

class MetagameEventOps:
    def startTerritoryInstance(instance: TerritoryInstance, channel: BlockingChannel):
        print('Starting Territory instance')
        queueName = f'aggregator-{instance.world}-MetagameEvent'
        RabbitConnection.declareQueue(queueName, channel)

        metagameEvent = MetagameEvent(
            str(instance.censusInstanceId),
            str(MetagameEventType.INDAR_ENLIGHTENMENT.value),
            str(MetagameEventState.STARTED.value),
            'started',
            str(instance.world.value),
            str(instance.zone.value),
            str(int(datetime.fromisoformat(instance.timeStarted).timestamp()))
        )

        message = RabbitCensusMessage(
            metagameEvent.event_name,
            metagameEvent.world_id,
            asdict(metagameEvent)
        )

        RabbitConnection.publishMessage(
            queueName,
            channel,
            message
        )

        print('Metagame Published!')

    def endTerritoryInstance(instance: TerritoryInstance, channel: BlockingChannel):
        print('Ending Territory instance')
        queueName = f'aggregator-{instance.world}-MetagameEvent'
        RabbitConnection.declareQueue(queueName, channel)

        metagameEvent = MetagameEvent(
            str(instance.censusInstanceId),
            str(MetagameEventType.INDAR_ENLIGHTENMENT.value),
            str(MetagameEventState.STARTED.value),
            'ended',
            str(instance.world.value),
            str(instance.zone.value),
            str(int(datetime.fromisoformat(instance.timeStarted).timestamp()))
        )

        message = RabbitCensusMessage(
            metagameEvent.event_name,
            metagameEvent.world_id,
            asdict(metagameEvent)
        )

        RabbitConnection.publishMessage(
            queueName,
            channel,
            message
        )
