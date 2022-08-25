import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.credentials import PlainCredentials

class RabbitConnection:
    def __init__(self):
        self.connection: BlockingConnection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                credentials=PlainCredentials('guest', 'guest')
            )
        )
        self.channel: Channel = connection.channel()
        self.channel.confirm_delivery()

    def getChannel():
        return self.channel
