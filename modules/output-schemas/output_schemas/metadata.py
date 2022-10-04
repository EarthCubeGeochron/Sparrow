from typing import Optional
from pydantic import BaseModel
from typing import List, Union
from enum import Enum
from .base import Metadata


class Researcher(BaseModel):
    name: str
    email: Optional[str] = None
    orcid: Optional[str] = None


class Publication(Metadata):
    doi: str
    title: str
    author: List[Researcher]
    journal: str
    year: int
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None


class Organization(BaseModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None


class ContributionType(Enum):
    SPONSOR = "sponsor"
    INVESTIGATOR = "investigator"
    AUTHOR = "author"
    EDITOR = "editor"
    COMPILER = "compiler"
    ARCHIVE = "archive"
    INDEXER = "indexer"
    PUBLISHER = "publisher"


class Contribution(Metadata):
    contributor: Union[Researcher, Organization]
    type: ContributionType
    details: Optional[str] = None
