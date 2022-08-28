from dataclass import RabbitCensusMessage
from service import Logger, RabbitConnection
from events import StreamEvent
log = Logger.getLogger()

class RabbitService:
    _connection: RabbitConnection = None

    def __init__(self, connection: RabbitConnection):
        self._connection = connection

    def send(
        self,
        event: StreamEvent,
        queueName: str
    ):
        log.debug(f"Sending message to Rabbit queue {queueName}:\n{event.to_json()}")

        self._connection.declareQueue(queueName)

        message = RabbitCensusMessage(
            event.event_name,
            event.world_id,
            event.to_json()
        )

        self._connection.publishMessage(
            queueName,
            message
        )

rabbit = RabbitService(RabbitConnection())