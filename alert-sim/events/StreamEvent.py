from datetime import datetime


class StreamEvent:
    event_name: str
    world_id: str
    timestamp: str = ""

    def __post_init__(self):
        if self.timestamp == "":
            self.timestamp = str(int(datetime.now().timestamp()))