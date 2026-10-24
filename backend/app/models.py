import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, LargeBinary, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    patient_code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    date_of_birth: Mapped[date] = mapped_column(Date)
    sex_or_gender: Mapped[str | None] = mapped_column(String(50))
    phone: Mapped[str | None] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RecordEntry(Base):
    """An official, staff-created entry in a patient's record."""

    __tablename__ = "record_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    visit_date: Mapped[date] = mapped_column(Date)
    record_type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(200))
    details: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(String(100))
    # Set when the entry came from an approved ExternalRecord. Plain column (no FK
    # constraint) because create_all can't alter an existing table.
    source_external_record_id: Mapped[uuid.UUID | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ExternalRecord(Base):
    """A patient-uploaded document from another facility. Never official until approved."""

    __tablename__ = "external_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    original_filename: Mapped[str] = mapped_column(String(120))
    content_type: Mapped[str] = mapped_column(String(50))
    size_bytes: Mapped[int] = mapped_column(Integer)
    # Original file kept in Postgres so it survives Render restarts.
    # Deferred: only loaded by the /file endpoints, not by list queries.
    file_data: Mapped[bytes] = mapped_column(LargeBinary, deferred=True)
    source_facility: Mapped[str | None] = mapped_column(String(200))
    document_date: Mapped[date | None] = mapped_column(Date)
    document_type: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    extraction_status: Mapped[str] = mapped_column(String(20), default="not_available")
    review_status: Mapped[str] = mapped_column(String(20), default="pending_review", index=True)
    review_note: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[str | None] = mapped_column(String(100))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    patient: Mapped[Patient] = relationship(lazy="joined", innerjoin=True)

    @property
    def patient_code(self) -> str:
        return self.patient.patient_code

    @property
    def patient_name(self) -> str:
        return self.patient.full_name
