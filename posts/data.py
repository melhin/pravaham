from dataclasses import dataclass
from enum import Enum


class EventType(Enum):
    NEW_POST = "new_post"
    ONLINE = "online"
    OFFLINE = "offline"


@dataclass
class DataToSend:
    event_type: EventType
    event_at: str
    text: str
