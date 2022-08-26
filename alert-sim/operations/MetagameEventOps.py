from dataclasses import asdict
from datetime import datetime
from pika.adapters.blocking_connection import BlockingChannel
from time import sleep
import sys
sys.path.append("..") # Adds higher directory to python modules path. This is so dumb.

from constants import AlertState, MetagameEventType, MetagameEventState
from dataclass import RabbitCensusMessage, TerritoryInstance
from events import MetagameEvent
from service import Logger
log = Logger.getLogger()
from .Ps2AlertsApiOps import Ps2AlertsApiOps
from .RabbitOps import RabbitOps

class MetagameEventOps:
    def startTerritoryInstance(instance: TerritoryInstance, channel: BlockingChannel):
        log.info('Starting Territory instance')
        queueName = f'aggregator-{instance.world}-MetagameEvent'

        metagameEvent = MetagameEvent(
            str(instance.censusInstanceId),
            str(MetagameEventType.INDAR_ENLIGHTENMENT.value),
            str(MetagameEventState.STARTED.value),
            'started',
            str(instance.world.value),
            str(instance.zone.value),
            str(int(datetime.fromisoformat(instance.timeStarted).timestamp()))
        )

        RabbitOps.send(metagameEvent, queueName, channel)

        log.info('Metagame Published! Waiting 5s for processing...')
        sleep(5)
        log.info('Checking metagame was accepted...')
        instanceData = Ps2AlertsApiOps.get('/instances/' + instance.instanceId)
        assert instanceData['state'] == AlertState.STARTED, 'Alert did not start correctly!'

    def endTerritoryInstance(instance: TerritoryInstance, channel: BlockingChannel):
        log.info('Ending Territory instance')
        queueName = f'aggregator-{instance.world}-MetagameEvent'

        metagameEvent = MetagameEvent(
            str(instance.censusInstanceId),
            str(MetagameEventType.INDAR_ENLIGHTENMENT.value),
            str(MetagameEventState.STARTED.value),
            'ended',
            str(instance.world.value),
            str(instance.zone.value),
            str(int(datetime.fromisoformat(instance.timeStarted).timestamp()))
        )

        RabbitOps.send(metagameEvent, queueName, channel)

        log.info('Metagame Published! Waiting 5s for processing...')
        sleep(5)
        log.info('Checking metagame was ended...')
        instanceData = Ps2AlertsApiOps.get('/instances/' + instance.instanceId)
        assert instanceData['state'] == AlertState.ENDED, 'Alert did not end correctly!'
