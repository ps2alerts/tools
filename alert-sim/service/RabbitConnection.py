import pika
from typing import Dict
from pika.adapters.blocking_connection import BlockingChannel
from pika.credentials import PlainCredentials
from pika import frame
from pika import spec

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
            print("Queue does not exist?")
            print(ret)
            return
        print('Queue '+queueName+' declared!')

    def publishMessage(
        queueName: str,
        channel: BlockingChannel,
        event: Dict
    ):
        print("Publishing event:")
        print(json.dumps(event))
        try:
            channel.basic_publish(
                exchange='',
                routing_key=queueName,
                body=json.dumps(event),
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

        print('Event published!')
