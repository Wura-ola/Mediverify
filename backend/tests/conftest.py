"""Shared test setup.

Safety rules:
- Every test runs inside a database transaction that is rolled back afterwards,
  so nothing is ever committed to Neon (even though the app calls commit()).
- Auth settings are replaced with test-only values BEFORE the app is imported,
  so your real .env secrets are never used or needed (only DATABASE_URL is).
- Set TEST_DATABASE_URL to point the tests at a separate database / Neon branch.
"""

import os
import struct
import uuid
import zlib

import pytest
from dotenv import load_dotenv

load_dotenv()  # does not override variables already set in the environment

if os.getenv("TEST_DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]
if not os.getenv("DATABASE_URL"):
    pytest.exit("DATABASE_URL (or TEST_DATABASE_URL) must be set to run the tests", returncode=2)

STAFF_USERNAME = "test-staff"
STAFF_PASSWORD = "test-staff-password"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["DEMO_STAFF_USERNAME"] = STAFF_USERNAME
os.environ["DEMO_STAFF_PASSWORD"] = STAFF_PASSWORD

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.db import Base, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402


# --- Synthetic file fixtures (tiny but valid file signatures) ---


def make_png(width: int = 2, height: int = 2) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(kind + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)

    raw = b"".join(b"\x00" + b"\xff\x00\x00" * width for _ in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


PNG_BYTES = make_png()
PDF_BYTES = b"%PDF-1.4\n% Synthetic demo PDF\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"
JPEG_BYTES = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00synthetic-jpeg-body\xff\xd9"
HTML_BYTES = b"<html><script>alert(1)</script></html>"


# --- Database isolation ---


@pytest.fixture(scope="session", autouse=True)
def _tables():
    Base.metadata.create_all(bind=engine)  # idempotent; same as app startup


@pytest.fixture
def db_session():
    """A session whose commits only release a SAVEPOINT; the outer transaction
    is rolled back at the end of the test, discarding everything."""
    connection = engine.connect()
    outer = connection.begin()
    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
        autoflush=False,
        expire_on_commit=False,
    )
    try:
        yield session
    finally:
        session.close()
        outer.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# --- Auth / data helpers ---


@pytest.fixture
def staff_headers(client):
    r = client.post(
        "/api/v1/staff/login", json={"username": STAFF_USERNAME, "password": STAFF_PASSWORD}
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def make_patient(client, staff_headers):
    """Factory: register a synthetic patient with a unique name, return its JSON."""

    def _make(full_name: str | None = None, date_of_birth: str = "2000-01-01", **extra):
        body = {
            "full_name": full_name or f"Test Patient {uuid.uuid4().hex[:8]}",
            "date_of_birth": date_of_birth,
            **extra,
        }
        r = client.post("/api/v1/patients", json=body, headers=staff_headers)
        assert r.status_code == 201, r.text
        return r.json()

    return _make


@pytest.fixture
def login_patient(client):
    """Factory: log a patient in, return Authorization headers."""

    def _login(patient: dict):
        r = client.post(
            "/api/v1/patient/login",
            json={"patient_code": patient["patient_code"], "date_of_birth": patient["date_of_birth"]},
        )
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    return _login


@pytest.fixture
def patient(make_patient):
    return make_patient()


@pytest.fixture
def patient_headers(login_patient, patient):
    return login_patient(patient)
