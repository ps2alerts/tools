from time import sleep
from typing import List

from dataclass import TerritoryInstance
from events import DeathEvent
from service import Logger, rabbit
log = Logger.getLogger()

class DeathEventOps:
    def send(instance: TerritoryInstance, events: List[DeathEvent]):
        log.info('Sending deaths for instance #'+instance.instanceId+'...')
        queueName = f'aggregator-{instance.instanceId}-Death'

        for event in events:
            rabbit.send(event, queueName)

        log.info('Deaths Published! Waiting 2.5s for processing...')
        sleep(2.5)
        log.info('Checking Deaths were processed...')
#         instanceData = Ps2AlertsApiOps.get('/instances/' + instance.instanceId)
#         assert instanceData['state'] == AlertState.STARTED, 'Alert did not start correctly!'
