from typing import Optional
import pika
from pika import frame
from pika import spec
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.credentials import PlainCredentials
from pika.exceptions import UnroutableError

from dataclass import RabbitCensusMessage
from service import Logger
log = Logger.getLogger()

class RabbitConnection:
    _channel: Optional[BlockingChannel] = None
    _connection: Optional[BlockingConnection] = None

    def __init__(self):
        self._channel = self.getChannel()

    def getChannel(self) -> BlockingChannel:
        if self._channel:
            return self._channel
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                credentials=PlainCredentials('guest', 'guest')
            )
        )
        channel = self._connection.channel()
        channel.confirm_delivery()
        return channel

    def declareQueue(self, queueName: str):
        ret: frame.Method = self._channel.queue_declare(queue=queueName, passive=True)
        if type(ret.method) != spec.Queue.DeclareOk:
            log.critical("Queue does not exist!")
            print(ret)
            return
        log.debug('Queue ' + queueName + ' declared!')

    def publishMessage(
        self,
        queueName: str,
        message: RabbitCensusMessage
    ):
        log.debug("Publishing event:")
        log.debug(message)
        try:
            self._channel.basic_publish(
                exchange='',
                routing_key=queueName,
                body=message.to_json(),
                properties=pika.BasicProperties(
                    content_type='text/plain',
                    delivery_mode=1
                ),
                mandatory=True
            )
        except UnroutableError as e:
            log.error(e.messages[0].body)
            log.error(e.messages[0].method)
            log.error(e.messages[0].properties)
            return 1

        log.debug('Event published!')
