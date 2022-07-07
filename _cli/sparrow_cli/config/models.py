from pydantic import BaseModel
from enum import Enum


class Level(str, Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class Message(BaseModel):
    id: str
    text: str
    details: str = None
    level: str = Level.WARNING
