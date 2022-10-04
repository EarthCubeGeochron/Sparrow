from pydantic import BaseModel


class DescModel(BaseModel):
    type: str


class MetaModel(BaseModel):
    ...


class DataModel(BaseModel):
    ...
