from typing import Union, List
from enum import Enum
from pydantic import BaseModel


class Level(str, Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class Message(BaseModel):
    id: str
    text: str
    details: Union[str, List[str]] = None
    level: str = Level.WARNING
