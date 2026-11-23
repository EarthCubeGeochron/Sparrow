"""
The data a pipeline hands to Sparrow, written out as plain models.

These are the same nested records the import API accepts. Vocabulary terms
(materials, techniques, parameters, units) are plain strings: Sparrow creates a
term the first time it is used. Records are matched to existing ones by their
identifying fields, so loading the same record twice does not duplicate it.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, ClassVar, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


def _prune(value):
    # An empty list would read as "this record has none", not "not given"
    if isinstance(value, dict):
        pruned = {k: _prune(v) for k, v in value.items()}
        return {k: v for k, v in pruned.items() if v != []}
    if isinstance(value, list):
        return [_prune(v) for v in value]
    return value


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    def to_import_data(self) -> dict:
        """The record as JSON-compatible data for Sparrow's import API."""
        return _prune(self.model_dump(mode="json", exclude_none=True))


class TopLevelRecord(Record):
    """A record that can be loaded on its own."""

    # Name of the Sparrow model this record is loaded as
    model_name: ClassVar[str]


class Researcher(Record):
    name: str
    orcid: Optional[str] = None


class Publication(Record):
    doi: Optional[str] = None
    title: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    author: Optional[str] = None
    link: Optional[str] = None


class Instrument(Record):
    name: str
    description: Optional[str] = None


class Point(Record):
    """A GeoJSON point: longitude, then latitude, in WGS84."""

    type: str = Field(default="Point", pattern="^Point$")
    coordinates: tuple[float, float]


class DatumType(Record):
    """What a number measures, and in which unit."""

    parameter: str
    unit: str
    error_unit: Optional[str] = None
    error_metric: Optional[str] = None
    description: Optional[str] = None
    is_computed: Optional[bool] = None
    is_interpreted: Optional[bool] = None


class Datum(Record):
    """A single measured or derived value."""

    value: Decimal | float
    error: Optional[Decimal | float] = None
    type: DatumType
    is_bad: Optional[bool] = None
    is_accepted: Optional[bool] = None


class Attribute(Record):
    """A text value describing an analysis or session."""

    parameter: str
    value: str


class Analysis(Record):
    """One step, spot or aliquot within a session, with the data it produced."""

    analysis_type: Optional[str] = None
    analysis_name: Optional[str] = None
    # Position of the analysis within its session
    session_index: Optional[int] = None
    date: Optional[datetime] = None
    material: Optional[str] = None
    is_standard: Optional[bool] = None
    is_bad: Optional[bool] = None
    is_accepted: Optional[bool] = None
    is_interpreted: Optional[bool] = None
    note: Optional[str] = None
    # Unstructured values specific to a lab or instrument
    data: Optional[dict[str, Any]] = None
    datum: list[Datum] = Field(default_factory=list)
    attribute: list[Attribute] = Field(default_factory=list)


class Project(TopLevelRecord):
    model_name = "project"

    name: str
    description: Optional[str] = None
    embargo_date: Optional[datetime] = None
    researcher: list[Researcher] = Field(default_factory=list)
    publication: list[Publication] = Field(default_factory=list)


class Sample(TopLevelRecord):
    """A physical sample. Sessions on it can be nested here, or loaded
    separately as `Session` records that name the sample."""

    model_name = "sample"

    name: str
    igsn: Optional[str] = None
    lab_id: Optional[str] = None
    material: Optional[str] = None
    location: Optional[Point] = None
    location_name: Optional[str] = None
    location_precision: Optional[int] = None
    elevation: Optional[Decimal | float] = None
    depth: Optional[Decimal | float] = None
    embargo_date: Optional[datetime] = None
    note: Optional[str] = None
    data: Optional[dict[str, Any]] = None
    member_of: Optional["Sample"] = None
    researcher: list[Researcher] = Field(default_factory=list)
    session: list["Session"] = Field(default_factory=list)


class Session(TopLevelRecord):
    """A set of analyses made together: one sample on one instrument."""

    model_name = "session"

    date: datetime
    name: Optional[str] = None
    uuid: Optional[UUID] = None
    end_date: Optional[datetime] = None
    technique: Optional[str] = None
    instrument: Optional[Instrument] = None
    target: Optional[str] = None
    sample: Optional[Sample] = None
    project: Optional[Project] = None
    publication: Optional[Publication] = None
    embargo_date: Optional[datetime] = None
    note: Optional[str] = None
    data: Optional[dict[str, Any]] = None
    analysis: list[Analysis] = Field(default_factory=list)
    attribute: list[Attribute] = Field(default_factory=list)


Sample.model_rebuild()

top_level_records: dict[str, type[TopLevelRecord]] = {
    cls.model_name: cls for cls in (Project, Sample, Session)
}
