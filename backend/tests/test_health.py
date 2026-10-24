"""Health check, app wiring (CORS, docs, routes) and test isolation itself."""

import uuid

from sqlalchemy import create_engine, func, select

from app import config
from app.db import engine
from app.models import Patient
from app.routers import health


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "database": "ok"}


def test_health_reports_database_down_without_leaking_details(client, monkeypatch):
    bad = create_engine("postgresql+psycopg://u:secret-pw@127.0.0.1:1/x?connect_timeout=1")
    monkeypatch.setattr(health, "engine", bad)
    r = client.get("/health")
    assert r.status_code == 503
    assert r.json() == {"status": "degraded", "database": "unavailable"}
    assert "secret-pw" not in r.text and "127.0.0.1" not in r.text


def test_docs_and_openapi_available(client):
    assert client.get("/docs").status_code == 200
    paths = client.get("/openapi.json").json()["paths"]
    operations = sum(len(methods) for methods in paths.values())
    assert operations == 18  # every endpoint in API_CONTRACT.md


def test_cors_allows_configured_origin(client):
    origin = config.CORS_ORIGINS[0]
    r = client.get("/health", headers={"Origin": origin})
    assert r.headers.get("access-control-allow-origin") == origin


def test_cors_preflight_for_configured_origin(client):
    origin = config.CORS_ORIGINS[0]
    r = client.options(
        "/api/v1/patients",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == origin


def test_cors_rejects_unknown_origin(client):
    r = client.get("/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in r.headers


def test_unknown_route_is_404(client):
    assert client.get("/no-such-route").status_code == 404


# --- The isolation guarantee the whole suite relies on ---

_MARKER = f"Isolation Check {uuid.uuid4().hex}"


def test_isolation_step1_create(make_patient):
    make_patient(full_name=_MARKER)


def test_isolation_step2_nothing_was_committed():
    # Runs on a fresh connection outside any test transaction.
    with engine.connect() as conn:
        count = conn.scalar(select(func.count()).select_from(Patient).where(Patient.full_name == _MARKER))
    assert count == 0
