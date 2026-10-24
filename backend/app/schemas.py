import uuid
from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


def _blank_to_none(v):
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


class PatientCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    date_of_birth: date
    sex_or_gender: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=30)

    @field_validator("full_name", mode="before")
    @classmethod
    def strip_name(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("sex_or_gender", "phone", mode="before")
    @classmethod
    def optional_blank(cls, v):
        return _blank_to_none(v)

    @field_validator("date_of_birth")
    @classmethod
    def not_in_future(cls, v: date):
        if v > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return v


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_code: str
    full_name: str
    date_of_birth: date
    sex_or_gender: str | None
    phone: str | None
    created_at: datetime

    @field_serializer("created_at")
    def utc(self, v: datetime):
        return v.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class VisitCreate(BaseModel):
    visit_date: date
    # external_import is reserved for approved external records, not manual entry.
    record_type: Literal["visit_note", "diagnosis", "prescription", "lab_result"] = "visit_note"
    title: str = Field(min_length=1, max_length=200)
    details: str | None = Field(default=None, max_length=5000)

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("details", mode="before")
    @classmethod
    def optional_blank(cls, v):
        return _blank_to_none(v)

    @field_validator("visit_date")
    @classmethod
    def not_in_future(cls, v: date):
        if v > date.today():
            raise ValueError("visit_date cannot be in the future")
        return v


class RecordEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    visit_date: date
    record_type: str
    title: str
    details: str | None
    created_by: str
    source_external_record_id: uuid.UUID | None
    created_at: datetime

    @field_serializer("created_at")
    def utc(self, v: datetime):
        return v.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class ExternalRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    patient_code: str
    patient_name: str
    original_filename: str
    content_type: str
    size_bytes: int
    source_facility: str | None
    document_date: date | None
    document_type: str | None
    notes: str | None
    extraction_status: str
    review_status: str
    review_note: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    uploaded_at: datetime

    @field_serializer("reviewed_at", "uploaded_at")
    def utc(self, v: datetime | None):
        if v is None:
            return None
        return v.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class ReviewBody(BaseModel):
    review_note: str | None = Field(default=None, max_length=1000)

    @field_validator("review_note", mode="before")
    @classmethod
    def optional_blank(cls, v):
        return _blank_to_none(v)


class StaffLogin(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class PatientLogin(BaseModel):
    patient_code: str = Field(min_length=1, max_length=16)
    date_of_birth: date

    @field_validator("patient_code", mode="before")
    @classmethod
    def normalise_code(cls, v):
        return v.strip().upper() if isinstance(v, str) else v


class StaffToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "staff"
    display_name: str = "Demo Staff"


class PatientToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "patient"
    patient: PatientOut
