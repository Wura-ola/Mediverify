"""External (patient-uploaded) records and staff review.

Uploads are kept separate from official RecordEntry rows. Only staff approval
creates an official entry, linked back via source_external_record_id.
"""

import re
import uuid
from datetime import date, datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session, undefer

from app.auth import require_patient, require_staff
from app.config import STAFF_DISPLAY_NAME
from app.db import get_db
from app.models import ExternalRecord, Patient, RecordEntry
from app.schemas import ExternalRecordOut, ReviewBody

MAX_UPLOAD_BYTES = 5 * 1024 * 1024

# Detect type from the file's first bytes; the client-sent Content-Type is not trusted.
_SIGNATURES = [
    (b"%PDF-", "application/pdf"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
]

patient_router = APIRouter(
    prefix="/api/v1/patients/me/external-records", tags=["external records (patient)"]
)
staff_router = APIRouter(
    prefix="/api/v1/staff/external-records",
    tags=["external records (staff)"],
    dependencies=[Depends(require_staff)],
)


def _detect_type(data: bytes) -> str | None:
    for magic, content_type in _SIGNATURES:
        if data.startswith(magic):
            return content_type
    return None


def _safe_filename(name: str | None) -> str:
    # Display only, never used as a storage path.
    base = (name or "").replace("\\", "/").rsplit("/", 1)[-1]
    base = re.sub(r"[^A-Za-z0-9._ -]", "_", base).strip(" .")
    return base[:100] or "upload"


def _optional_text(value: str | None, field: str, max_len: int) -> str | None:
    value = (value or "").strip()
    if len(value) > max_len:
        raise HTTPException(status_code=422, detail=f"{field} must be at most {max_len} characters")
    return value or None


def _parse_document_date(value: str | None) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        raise HTTPException(status_code=422, detail="document_date must be YYYY-MM-DD")
    if parsed > date.today():
        raise HTTPException(status_code=422, detail="document_date cannot be in the future")
    return parsed


def _file_response(record: ExternalRecord) -> Response:
    return Response(
        content=record.file_data,
        media_type=record.content_type,
        headers={
            "Content-Disposition": f'inline; filename="{record.original_filename}"',
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "private, no-store",
        },
    )


# --- Patient ---


@patient_router.post("", response_model=ExternalRecordOut, status_code=status.HTTP_201_CREATED)
async def upload_external_record(
    file: UploadFile = File(...),
    source_facility: str | None = Form(None),
    document_date: str | None = Form(None, description="YYYY-MM-DD"),
    document_type: str | None = Form(None),
    notes: str | None = Form(None),
    patient: Patient = Depends(require_patient),
    db: Session = Depends(get_db),
):
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is larger than 5 MB")
    if not data:
        raise HTTPException(status_code=422, detail="File is empty")
    content_type = _detect_type(data)
    if content_type is None:
        raise HTTPException(status_code=415, detail="Only PDF, PNG or JPEG files are allowed")

    record = ExternalRecord(
        patient_id=patient.id,
        original_filename=_safe_filename(file.filename),
        content_type=content_type,
        size_bytes=len(data),
        file_data=data,
        source_facility=_optional_text(source_facility, "source_facility", 200),
        document_date=_parse_document_date(document_date),
        document_type=_optional_text(document_type, "document_type", 50),
        notes=_optional_text(notes, "notes", 5000),
    )
    db.add(record)
    db.commit()
    return db.get(ExternalRecord, record.id)


@patient_router.get("", response_model=list[ExternalRecordOut])
def my_external_records(patient: Patient = Depends(require_patient), db: Session = Depends(get_db)):
    stmt = (
        select(ExternalRecord)
        .where(ExternalRecord.patient_id == patient.id)
        .order_by(ExternalRecord.uploaded_at.desc())
    )
    return db.scalars(stmt).all()


@patient_router.get("/{record_id}/file")
def my_external_record_file(
    record_id: uuid.UUID, patient: Patient = Depends(require_patient), db: Session = Depends(get_db)
):
    stmt = (
        select(ExternalRecord)
        .options(undefer(ExternalRecord.file_data))
        .where(ExternalRecord.id == record_id, ExternalRecord.patient_id == patient.id)
    )
    record = db.scalar(stmt)
    if record is None:  # also covers "belongs to another patient"
        raise HTTPException(status_code=404, detail="External record not found")
    return _file_response(record)


# --- Staff ---


def _get_or_404(db: Session, record_id: uuid.UUID, *, for_update=False, with_file=False):
    stmt = select(ExternalRecord).where(ExternalRecord.id == record_id)
    if with_file:
        stmt = stmt.options(undefer(ExternalRecord.file_data))
    if for_update:
        stmt = stmt.with_for_update(of=ExternalRecord)
    record = db.scalar(stmt)
    if record is None:
        raise HTTPException(status_code=404, detail="External record not found")
    return record


@staff_router.get("", response_model=list[ExternalRecordOut])
def list_external_records(
    status_filter: Literal["pending_review", "approved", "rejected"] | None = Query(
        default=None, alias="status"
    ),
    db: Session = Depends(get_db),
):
    stmt = select(ExternalRecord).order_by(ExternalRecord.uploaded_at.desc()).limit(200)
    if status_filter:
        stmt = stmt.where(ExternalRecord.review_status == status_filter)
    return db.scalars(stmt).all()


@staff_router.get("/{record_id}", response_model=ExternalRecordOut)
def get_external_record(record_id: uuid.UUID, db: Session = Depends(get_db)):
    return _get_or_404(db, record_id)


@staff_router.get("/{record_id}/file")
def get_external_record_file(record_id: uuid.UUID, db: Session = Depends(get_db)):
    return _file_response(_get_or_404(db, record_id, with_file=True))


def _review(db: Session, record_id: uuid.UUID, decision: str, body: ReviewBody) -> ExternalRecord:
    # Row lock so two reviewers can't both approve (and create two official entries).
    record = _get_or_404(db, record_id, for_update=True)
    if record.review_status != "pending_review":
        raise HTTPException(status_code=409, detail=f"Already reviewed ({record.review_status})")
    record.review_status = decision
    record.review_note = body.review_note
    record.reviewed_by = STAFF_DISPLAY_NAME
    record.reviewed_at = datetime.now(timezone.utc)
    if decision == "approved":
        source = record.source_facility or "unknown facility"
        kind = record.document_type or "document"
        db.add(
            RecordEntry(
                patient_id=record.patient_id,
                visit_date=record.document_date or record.uploaded_at.date(),
                record_type="external_import",
                title=f"External {kind} from {source}"[:200],
                details=record.notes,
                created_by=STAFF_DISPLAY_NAME,
                source_external_record_id=record.id,
            )
        )
    db.commit()
    return db.get(ExternalRecord, record.id)


@staff_router.post("/{record_id}/approve", response_model=ExternalRecordOut)
def approve_external_record(record_id: uuid.UUID, body: ReviewBody, db: Session = Depends(get_db)):
    return _review(db, record_id, "approved", body)


@staff_router.post("/{record_id}/reject", response_model=ExternalRecordOut)
def reject_external_record(record_id: uuid.UUID, body: ReviewBody, db: Session = Depends(get_db)):
    return _review(db, record_id, "rejected", body)
