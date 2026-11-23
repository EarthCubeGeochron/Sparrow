from enum import Enum
from typing import List, Union

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
