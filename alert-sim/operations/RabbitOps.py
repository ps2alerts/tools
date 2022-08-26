from dataclasses import asdict
from pika.adapters.blocking_connection import BlockingChannel
import sys
sys.path.append("..") # Adds higher directory to python modules path. This is so dumb.
from typing import Dict

from dataclass import RabbitCensusMessage
from service import Logger, RabbitConnection
log = Logger.getLogger()

class RabbitOps:
    def send(
        event: Dict,
        queueName: str,
        channel: BlockingChannel
    ):
        log.debug('Sending message to Rabbit queue '+queueName+'...')
        log.debug(asdict(event))

        RabbitConnection.declareQueue(queueName, channel)

        message = RabbitCensusMessage(
            event.event_name,
            event.world_id,
            asdict(event)
        )

        RabbitConnection.publishMessage(
            queueName,
            channel,
            message
        )
