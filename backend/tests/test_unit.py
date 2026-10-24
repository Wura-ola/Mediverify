"""Pure-logic tests: config parsing, helpers and schema validation (no HTTP)."""

import re
from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import config
from app.routers import external_records as ext
from app.routers import patients
from app.schemas import PatientCreate, PatientLogin, PatientOut, ReviewBody, VisitCreate

from .conftest import HTML_BYTES, JPEG_BYTES, PDF_BYTES, PNG_BYTES

TOMORROW = (date.today() + timedelta(days=1)).isoformat()


# --- config ---


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("postgresql://u:p@h/db?sslmode=require", "postgresql+psycopg://u:p@h/db?sslmode=require"),
        ("postgres://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql+psycopg://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("  postgresql://u:p@h/db  ", "postgresql+psycopg://u:p@h/db"),
    ],
)
def test_database_url_rewritten_for_psycopg(monkeypatch, raw, expected):
    monkeypatch.setenv("DATABASE_URL", raw)
    assert config._database_url() == expected


def test_missing_database_url_gives_clear_error(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    with pytest.raises(RuntimeError, match="DATABASE_URL is not set"):
        config._database_url()


@pytest.mark.parametrize(
    "value, expected",
    [("", None), ("   ", None), ("change-me", None), ("change-me-to-a-long-random-string", None), ("real", "real")],
)
def test_secret_placeholders_count_as_unset(monkeypatch, value, expected):
    monkeypatch.setenv("SOME_SECRET", value)
    assert config._secret("SOME_SECRET") == expected


# --- patient code ---


def test_patient_code_format_and_alphabet():
    for _ in range(200):
        code = patients._new_patient_code()
        assert re.fullmatch(r"MV-[ABCDEFGHJKMNPQRSTUVWXYZ23456789]{8}", code), code


def test_patient_codes_are_random():
    codes = {patients._new_patient_code() for _ in range(500)}
    assert len(codes) == 500


# --- external record helpers ---


@pytest.mark.parametrize(
    "data, expected",
    [
        (PNG_BYTES, "image/png"),
        (PDF_BYTES, "application/pdf"),
        (JPEG_BYTES, "image/jpeg"),
        (HTML_BYTES, None),
        (b"GIF89a....", None),
        (b"", None),
    ],
)
def test_detect_type_uses_file_signature(data, expected):
    assert ext._detect_type(data) == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("report.pdf", "report.pdf"),
        ("../../evil<script>.png", "evil_script_.png"),
        ("C:\\Users\\x\\scan 1.jpg", "scan 1.jpg"),
        ("/etc/passwd", "passwd"),
        ("na\u00efve\u00e9.pdf", "na_ve_.pdf"),
        ("...", "upload"),
        ("", "upload"),
        (None, "upload"),
    ],
)
def test_safe_filename(name, expected):
    assert ext._safe_filename(name) == expected


def test_safe_filename_truncates_long_names():
    assert len(ext._safe_filename("a" * 500 + ".pdf")) == 100


def test_parse_document_date():
    assert ext._parse_document_date(None) is None
    assert ext._parse_document_date("   ") is None
    assert ext._parse_document_date(" 2024-03-02 ") == date(2024, 3, 2)


@pytest.mark.parametrize("bad", ["03/02/2024", "2024-13-01", "yesterday", TOMORROW])
def test_parse_document_date_rejects_invalid_or_future(bad):
    with pytest.raises(HTTPException) as exc:
        ext._parse_document_date(bad)
    assert exc.value.status_code == 422


def test_optional_text():
    assert ext._optional_text(None, "f", 10) is None
    assert ext._optional_text("   ", "f", 10) is None
    assert ext._optional_text("  hi  ", "f", 10) == "hi"
    with pytest.raises(HTTPException) as exc:
        ext._optional_text("x" * 11, "field_name", 10)
    assert exc.value.status_code == 422 and "field_name" in exc.value.detail


# --- schemas ---


def test_patient_create_normalises_input():
    p = PatientCreate(full_name="  Ada Example ", date_of_birth="2002-04-15", sex_or_gender=" ", phone="")
    assert p.full_name == "Ada Example"
    assert p.sex_or_gender is None and p.phone is None


@pytest.mark.parametrize(
    "body",
    [
        {"full_name": "", "date_of_birth": "2000-01-01"},
        {"full_name": "   ", "date_of_birth": "2000-01-01"},
        {"full_name": "x" * 201, "date_of_birth": "2000-01-01"},
        {"full_name": "Ok", "date_of_birth": TOMORROW},
        {"full_name": "Ok", "date_of_birth": "not-a-date"},
        {"full_name": "Ok"},
        {"full_name": "Ok", "date_of_birth": "2000-01-01", "phone": "1" * 31},
    ],
)
def test_patient_create_rejects_invalid(body):
    with pytest.raises(ValidationError):
        PatientCreate(**body)


def test_patient_out_serialises_timestamps_as_utc_z():
    out = PatientOut(
        id="00000000-0000-0000-0000-000000000001",
        patient_code="MV-AAAAAAAA",
        full_name="X",
        date_of_birth=date(2000, 1, 1),
        sex_or_gender=None,
        phone=None,
        created_at=datetime(2026, 1, 1, 13, 0, tzinfo=timezone(timedelta(hours=1))),
    )
    assert out.model_dump(mode="json")["created_at"] == "2026-01-01T12:00:00Z"


def test_visit_create_defaults_and_rules():
    v = VisitCreate(visit_date="2026-01-01", title="  Check-up ", details="  ")
    assert v.record_type == "visit_note" and v.title == "Check-up" and v.details is None
    for bad in (
        {"record_type": "external_import"},
        {"record_type": "surgery"},
        {"visit_date": TOMORROW},
        {"title": "  "},
        {"title": "x" * 201},
        {"details": "x" * 5001},
    ):
        with pytest.raises(ValidationError):
            VisitCreate(**{"visit_date": "2026-01-01", "title": "t", **bad})


def test_patient_login_normalises_code():
    assert PatientLogin(patient_code="  mv-abcd2345 ", date_of_birth="2000-01-01").patient_code == "MV-ABCD2345"


def test_review_body():
    assert ReviewBody().review_note is None
    assert ReviewBody(review_note="   ").review_note is None
    with pytest.raises(ValidationError):
        ReviewBody(review_note="x" * 1001)
