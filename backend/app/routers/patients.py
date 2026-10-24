import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import require_patient, require_staff
from app.config import STAFF_DISPLAY_NAME
from app.db import get_db
from app.models import Patient, RecordEntry
from app.schemas import PatientCreate, PatientOut, RecordEntryOut, VisitCreate

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])
staff_only = [Depends(require_staff)]

# No 0/O or 1/I/L, so codes are easy to read out loud and type.
_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def _new_patient_code() -> str:
    return "MV-" + "".join(secrets.choice(_CODE_ALPHABET) for _ in range(8))


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED, dependencies=staff_only)
def register_patient(body: PatientCreate, db: Session = Depends(get_db)):
    # Retry on the (very unlikely) chance of a patient_code collision.
    for _ in range(5):
        patient = Patient(patient_code=_new_patient_code(), **body.model_dump())
        db.add(patient)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue
        db.refresh(patient)
        return patient
    raise HTTPException(status_code=500, detail="Could not generate a unique Patient ID, try again")


@router.get("", response_model=list[PatientOut], dependencies=staff_only)
def list_patients(
    q: str | None = Query(default=None, max_length=100, description="Part of name or Patient ID"),
    db: Session = Depends(get_db),
):
    stmt = select(Patient).order_by(Patient.created_at.desc()).limit(100)
    if q and q.strip():
        term = q.strip().lower()
        stmt = stmt.where(
            or_(
                func.lower(Patient.full_name).contains(term, autoescape=True),
                func.lower(Patient.patient_code).contains(term, autoescape=True),
            )
        )
    return db.scalars(stmt).all()


def _records_for(db: Session, patient_id: uuid.UUID):
    stmt = (
        select(RecordEntry)
        .where(RecordEntry.patient_id == patient_id)
        .order_by(RecordEntry.visit_date.desc(), RecordEntry.created_at.desc())
    )
    return db.scalars(stmt).all()


def _get_or_404(db: Session, patient_id: uuid.UUID) -> Patient:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


# --- Patient's own view. Declared before /{patient_id} so "me" isn't parsed as a UUID. ---
# The patient comes from the token only; there is no way to ask for someone else's ID.


@router.get("/me", response_model=PatientOut)
def my_profile(patient: Patient = Depends(require_patient)):
    return patient


@router.get("/me/records", response_model=list[RecordEntryOut])
def my_records(patient: Patient = Depends(require_patient), db: Session = Depends(get_db)):
    return _records_for(db, patient.id)


# --- Staff routes for a specific patient ---


@router.get("/{patient_id}", response_model=PatientOut, dependencies=staff_only)
def get_patient(patient_id: uuid.UUID, db: Session = Depends(get_db)):
    return _get_or_404(db, patient_id)


@router.post(
    "/{patient_id}/visits",
    response_model=RecordEntryOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=staff_only,
)
def add_visit(patient_id: uuid.UUID, body: VisitCreate, db: Session = Depends(get_db)):
    _get_or_404(db, patient_id)
    entry = RecordEntry(patient_id=patient_id, created_by=STAFF_DISPLAY_NAME, **body.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/{patient_id}/records", response_model=list[RecordEntryOut], dependencies=staff_only)
def patient_records(patient_id: uuid.UUID, db: Session = Depends(get_db)):
    _get_or_404(db, patient_id)
    return _records_for(db, patient_id)
