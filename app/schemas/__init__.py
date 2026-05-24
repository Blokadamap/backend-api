"""Pydantic v2 schemas for backend-api proxy endpoints.

Request schemas mirror database-core DTOs exactly.
Response schemas represent the shapes returned by database-core GET endpoints.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, RootModel, model_validator


# ---------------------------------------------------------------------------
# Common
# ---------------------------------------------------------------------------

class SexEnum(str, Enum):
    MALE = "M"
    FEMALE = "F"


class ErrorResponse(BaseModel):
    error: str


# ---------------------------------------------------------------------------
# Generic filter item (used by all filter endpoints)
# ExtendedBaseClass provides: id (int) + name (str)
# ---------------------------------------------------------------------------

class FilterItem(BaseModel):
    """A taxonomy item with id + name. database-core returns these as
    `{<table>_id: ..., name: ...}` (SQLAlchemy column names); this validator
    folds the *_id field into `id` so the frontend gets a uniform shape.
    """
    id: int
    name: str

    @model_validator(mode="before")
    @classmethod
    def _fold_id(cls, data):
        if isinstance(data, dict) and "id" not in data:
            for key in data:
                if key.endswith("_id"):
                    data = {**data, "id": data[key]}
                    break
        return data


# ---------------------------------------------------------------------------
# Author — Request schemas
# ---------------------------------------------------------------------------

class AuthorCreate(BaseModel):
    last_name: str
    first_name: str
    middle_name: str
    sex: SexEnum
    birth_date: date
    biography: str
    has_children: bool
    family_status_id: int
    social_class_ids: List[int]
    nationality_ids: List[int]
    religion_ids: List[int]
    education_ids: List[int]
    occupation_ids: List[int]
    political_party_ids: List[int]
    card_ids: List[int]
    diary_started_at: date
    diary_finished_at: date
    diary_source: str


# ---------------------------------------------------------------------------
# Author — Response schemas
# ---------------------------------------------------------------------------

class AuthorShort(BaseModel):
    """extended=false or list items from GET /authors/"""
    author_id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str


class AuthorFilters(BaseModel):
    """GET /authors/filters"""
    family_statuses: List[FilterItem]
    social_classes: List[FilterItem]
    nationalities: List[FilterItem]
    religions: List[FilterItem]
    educations: List[FilterItem]
    occupations: List[FilterItem]
    political_parties: List[FilterItem]
    cards: List[FilterItem]


class AuthorResponse(BaseModel):
    """extended=true — full author with all relations.
    database-core returns the SQLAlchemy Author object with joined relations.
    """
    author_id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    sex: str
    birth_date: date
    biography: str
    has_children: bool
    family_status_id: int
    family_status: Optional[FilterItem] = None
    social_classes: List[FilterItem] = []
    nationalities: List[FilterItem] = []
    religions: List[FilterItem] = []
    education: List[FilterItem] = []
    occupation: List[FilterItem] = []
    political_parties: List[FilterItem] = []
    cards: List[FilterItem] = []
    diary_started_at: Optional[date] = None
    diary_finished_at: Optional[date] = None
    diary_source: Optional[str] = None


# ---------------------------------------------------------------------------
# Note — Request schemas
# ---------------------------------------------------------------------------

class NoteToPointCreate(BaseModel):
    point_id: int
    description: str


class NoteCreate(BaseModel):
    author_id: int
    note_type_id: int
    temporality_id: int
    created_at: date
    citation: str
    source: str
    tag_ids: List[int]
    note_to_points: List[NoteToPointCreate]


class TagCreate(BaseModel):
    name: str


# ---------------------------------------------------------------------------
# Note — Response schemas
# ---------------------------------------------------------------------------

class NoteShort(BaseModel):
    """extended=false — note with author name."""
    note_id: int
    citation: str
    created_at: date
    first_name: str
    middle_name: Optional[str] = None
    last_name: str


class NoteFilters(BaseModel):
    """GET /notes/filters"""
    tags: List[FilterItem]
    note_types: List[FilterItem]
    temporalities: List[FilterItem]


class PointInNote(BaseModel):
    """Point as embedded in NoteDetailed response."""
    point_id: int
    name: str
    description: Optional[str] = None
    point_coordinates: List[dict[str, Any]] = []


class NoteResponse(BaseModel):
    """extended=true — full note with relations."""
    note_id: int
    diary_id: int
    note_type_id: int
    temporality_id: int
    created_at: date
    citation: str
    source: str
    note_type: Optional[FilterItem] = None
    temporality: Optional[FilterItem] = None
    tags: List[FilterItem] = []
    first_name: str = ""
    middle_name: Optional[str] = None
    last_name: str = ""
    note_to_points: List[dict[str, Any]] = []


class NoteDetailed(BaseModel):
    """GET /notes/detailed/{id} — note with full author and point details."""
    note_id: int
    diary_id: int
    note_type_id: int
    temporality_id: int
    created_at: date
    citation: str
    source: str
    note_type: Optional[FilterItem] = None
    temporality: Optional[FilterItem] = None
    tags: List[FilterItem] = []
    points: List[PointInNote] = []
    # Author fields (joined from Author model)
    author_id: int
    author_first_name: str = ""
    author_middle_name: Optional[str] = None
    author_last_name: str = ""
    author_sex: Optional[str] = None
    author_birth_date: Optional[date] = None
    author_biography: Optional[str] = None
    author_has_children: Optional[bool] = None
    author_family_status_id: Optional[int] = None
    author_education: list = []
    author_family_status: Optional[FilterItem] = None


# ---------------------------------------------------------------------------
# Point — Request schemas
# ---------------------------------------------------------------------------

class PointCreate(BaseModel):
    rayon_id: int
    street: str
    building: str
    latitude: float
    longitude: Optional[float] = None
    point_type_id: int
    point_subtype_id: Optional[int] = None
    point_subsubtype_id: Optional[int] = None
    name: str
    description: Optional[str] = None


class CoordinatesCreate(BaseModel):
    latitude: float
    longitude: float


# ---------------------------------------------------------------------------
# Point — Response schemas
# ---------------------------------------------------------------------------

class PointShort(BaseModel):
    """extended=false — point with type metadata."""
    point_id: int
    name: str
    has_fixed_coordinates: bool
    has_address: bool


class CoordinateItem(BaseModel):
    latitude: float
    longitude: float


class PointCoordinatesResponse(BaseModel):
    """GET /points/{id}/coordinates"""
    point_id: int
    coordinates: List[CoordinateItem]


class PointSubSubTypeItem(BaseModel):
    point_subsubtype_id: int
    name: str
    point_subtype_id: Optional[int] = None


class PointSubTypeItem(BaseModel):
    point_subtype_id: int
    name: str
    point_type_id: Optional[int] = None
    point_subsubtypes: List[PointSubSubTypeItem] = []


class PointTypeItem(BaseModel):
    point_type_id: int
    name: str
    has_fixed_coordinates: bool
    has_address: bool
    point_subtypes: List[PointSubTypeItem] = []


class PointFilters(RootModel[List[PointTypeItem]]):
    """GET /points/filters — type hierarchy with nested subtypes."""
    pass


class PointResponse(BaseModel):
    """extended=true — full point with all relations."""
    point_id: int
    name: str
    rayon_id: int
    street: str
    building: str
    point_type_id: int
    point_subtype_id: Optional[int] = None
    point_subsubtype_id: Optional[int] = None
    description: Optional[str] = None
    rayon: Optional[FilterItem] = None
    point_type: Optional[PointTypeItem] = None
    point_subtype: Optional[PointSubTypeItem] = None
    point_subsubtype: Optional[PointSubSubTypeItem] = None
    point_coordinates: List[CoordinateItem] = []


# ---------------------------------------------------------------------------
# Diary — Response schemas
# ---------------------------------------------------------------------------

class DiaryShort(BaseModel):
    """Short diary info."""
    diary_id: int
    author_id: int
    diary_started_at: Optional[date] = None
    diary_finished_at: Optional[date] = None
    diary_source: Optional[str] = None


class DiaryResponse(DiaryShort):
    """Full diary with author details."""
    author: Optional[AuthorShort] = None


class DiaryCreate(BaseModel):
    started_at: date
    finished_at: date
    source: str
    author_id: int


# ---------------------------------------------------------------------------
# Taxonomy CUD schemas
# ---------------------------------------------------------------------------

class NamedCreate(BaseModel):
    name: str


class PointTypeCreate(BaseModel):
    name: str
    has_fixed_coordinates: bool
    has_address: bool


class PointSubTypeCreate(BaseModel):
    name: str
    point_type_id: Optional[int] = None


class PointSubSubTypeCreate(BaseModel):
    name: str
    point_subtype_id: Optional[int] = None
