from dataclasses import asdict
from pika.adapters.blocking_connection import BlockingChannel
import sys
sys.path.append("..") # Adds higher directory to python modules path. This is so dumb.

from dataclass import RabbitCensusMessage, TerritoryInstance
from events import DeathEvebt
from service import Logger
log = Logger.getLogger()
from .Ps2AlertsApiOps import Ps2AlertsApiOps
from .RabbitOps import RabbitOps

class DeathEventOps:
    def send(instance: TerritoryInstance, events: List[DeathEvent], channel: BlockingChannel):
        log.info('Sending deaths for instance #'+instance.instanceId+'...')
        queueName = f'aggregator-{instance.instanceId}-Death'

        for event in events:
            RabbitOps.send(event, queueName, channel)

        log.info('Deaths Published! Waiting 2.5s for processing...')
        sleep(2.5)
        log.info('Checking Deaths were processed...')
#         instanceData = Ps2AlertsApiOps.get('/instances/' + instance.instanceId)
#         assert instanceData['state'] == AlertState.STARTED, 'Alert did not start correctly!'
