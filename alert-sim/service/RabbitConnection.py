from typing import Dict
import json
import pika
from pika import frame
from pika import spec
from pika.adapters.blocking_connection import BlockingChannel
from pika.credentials import PlainCredentials
import sys
sys.path.append("..") # Adds higher directory to python modules path. This is so dumb.

from dataclass import RabbitCensusMessage
from service import Logger
log = Logger.getLogger()

class RabbitConnection:
    def getChannel():
        connection: BlockingConnection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                credentials=PlainCredentials('guest', 'guest')
            )
        )
        channel = connection.channel()
        channel.confirm_delivery()
        return channel

    # I can't figure out how to make this self reference a connection, so we have to pass it in
    def declareQueue(queueName: str, channel: BlockingChannel):
        ret: frame.Method = channel.queue_declare(queue=queueName, passive=True)
        if type(ret.method) != spec.Queue.DeclareOk:
            log.critical("Queue does not exist!")
            print(ret)
            return
        log.debug('Queue '+queueName+' declared!')

    def publishMessage(
        queueName: str,
        channel: BlockingChannel,
        message: RabbitCensusMessage
    ):
        log.debug("Publishing event:")
        log.debug(message)
        try:
            channel.basic_publish(
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
            print(e.messages[0].body)
            print(e.messages[0].method)
            print(e.messages[0].properties)
            return 1

        log.debug('Event published!')
