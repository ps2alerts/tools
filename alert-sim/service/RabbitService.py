from dataclass import RabbitCensusMessage
from service import Logger, RabbitConnection
from events import StreamEvent
log = Logger.getLogger("RabbitService")

class RabbitService:
    _connection: RabbitConnection = None

    def __init__(self, connection: RabbitConnection):
        self._connection = connection

    def send(
        self,
        event: StreamEvent,
        queueName: str
    ):
        log.debug(f"Sending message to Rabbit queue {queueName}")

        self._connection.declareQueue(queueName)

        message = RabbitCensusMessage(
            event.event_name,
            event.world_id,
            event
        )

        self._connection.publishMessage(
            queueName,
            message
        )

rabbit = None
def get_rabbit():
    global rabbit
    if rabbit:
        return rabbit
    rabbit = RabbitService(RabbitConnection())
    return rabbit