from pika.adapters.blocking_connection import BlockingChannel
from dataclasses import asdict
from datetime import datetime
from time import sleep
import sys
sys.path.append("..") # Adds higher directory to python modules path. This is so dumb.

from constants import AlertState, MetagameEventType, MetagameEventState
from dataclass import RabbitCensusMessage, TerritoryInstance
from events import MetagameEvent
from service import Logger, RabbitConnection
from .Ps2AlertsApiOps import Ps2AlertsApiOps
log = Logger.getLogger()

class MetagameEventOps:
    def startTerritoryInstance(instance: TerritoryInstance, channel: BlockingChannel):
        log.info('Starting Territory instance')
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

        log.info('Metagame Published! Waiting 5s for processing...')
        sleep(5)
        log.info('Checking metagame was accepted...')
        instanceData = Ps2AlertsApiOps.get('/instances/' + instance.instanceId)
        assert instanceData['state'] == AlertState.STARTED, 'Alert did not start correctly!'

    def endTerritoryInstance(instance: TerritoryInstance, channel: BlockingChannel):
        log.info('Ending Territory instance')
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

        log.info('Metagame Published! Waiting 5s for processing...')
        sleep(5)
        log.info('Checking metagame was ended...')
        instanceData = Ps2AlertsApiOps.get('/instances/' + instance.instanceId)
        assert instanceData['state'] == AlertState.ENDED, 'Alert did not end correctly!'
