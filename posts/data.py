from dataclasses import dataclass
from enum import Enum


class EventType(Enum):
    NEW_POST = "new_post"
    USER_CONNECT = "user_connect"
    USER_DISCONNECT = "user_disconnect"


@dataclass
class DataToSend:
    event_type: EventType
    event_at: str
    text: str
