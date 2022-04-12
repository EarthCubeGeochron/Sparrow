from typing import Optional
from pydantic import BaseModel
from decimal import Decimal
from typing import List


class Datum(BaseModel):
    value: Decimal
    error: Optional[Decimal] = None
    unit: str


class DescModel(BaseModel):
    type: str


class SampleModel(BaseModel):
    name: str
    id: str
    igsn: Optional[str] = None


class DataModel(BaseModel):
    sample: SampleModel
    meta: List[BaseModel]
    info: List[BaseModel]
