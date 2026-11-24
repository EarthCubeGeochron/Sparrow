from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel


class Level(str, Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class Message(BaseModel):
    id: str
    text: str
    details: Optional[Union[str, List[str]]] = None
    level: str = Level.WARNING
