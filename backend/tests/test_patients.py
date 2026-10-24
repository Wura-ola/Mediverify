"""Patient registration, list/search and detail (staff only)."""

import re
import uuid
from datetime import datetime, timedelta, timezone

from app.models import Patient
from app.routers import patients as patient_routes

CODE_RE = r"MV-[ABCDEFGHJKMNPQRSTUVWXYZ23456789]{8}"


def test_register_patient(client, staff_headers):
    body = {"full_name": "  Ada Example ", "date_of_birth": "2002-04-15", "sex_or_gender": "Female", "phone": "08000000000"}
    r = client.post("/api/v1/patients", json=body, headers=staff_headers)
    assert r.status_code == 201
    p = r.json()
    assert set(p) == {"id", "patient_code", "full_name", "date_of_birth", "sex_or_gender", "phone", "created_at"}
    uuid.UUID(p["id"])
    assert re.fullmatch(CODE_RE, p["patient_code"])
    assert p["full_name"] == "Ada Example"
    assert p["date_of_birth"] == "2002-04-15"
    assert p["sex_or_gender"] == "Female" and p["phone"] == "08000000000"
    assert p["created_at"].endswith("Z")


def test_register_optional_fields_blank_become_null(client, staff_headers):
    r = client.post(
        "/api/v1/patients",
        json={"full_name": "Bola Sample", "date_of_birth": "1990-01-01", "sex_or_gender": "", "phone": "  "},
        headers=staff_headers,
    )
    assert r.status_code == 201
    assert r.json()["sex_or_gender"] is None and r.json()["phone"] is None


def test_register_validation_errors(client, staff_headers):
    for body in (
        {"date_of_birth": "2000-01-01"},
        {"full_name": "  ", "date_of_birth": "2000-01-01"},
        {"full_name": "x" * 201, "date_of_birth": "2000-01-01"},
        {"full_name": "Future Baby", "date_of_birth": "2999-01-01"},
        {"full_name": "Bad Date", "date_of_birth": "01-01-2000"},
    ):
        assert client.post("/api/v1/patients", json=body, headers=staff_headers).status_code == 422, body


def test_patient_codes_are_unique(make_patient):
    codes = {make_patient()["patient_code"] for _ in range(5)}
    assert len(codes) == 5


def test_register_retries_on_code_collision(client, staff_headers, make_patient, monkeypatch):
    taken = make_patient()["patient_code"]
    codes = iter([taken, taken, "MV-RETRY234"])
    monkeypatch.setattr(patient_routes, "_new_patient_code", lambda: next(codes))
    r = client.post("/api/v1/patients", json={"full_name": "Retry", "date_of_birth": "2000-01-01"}, headers=staff_headers)
    assert r.status_code == 201
    assert r.json()["patient_code"] == "MV-RETRY234"


def test_register_gives_up_after_repeated_collisions(client, staff_headers, make_patient, monkeypatch):
    taken = make_patient()["patient_code"]
    monkeypatch.setattr(patient_routes, "_new_patient_code", lambda: taken)
    r = client.post("/api/v1/patients", json={"full_name": "Unlucky", "date_of_birth": "2000-01-01"}, headers=staff_headers)
    assert r.status_code == 500
    assert "unique Patient ID" in r.json()["detail"]


def test_registration_requires_staff(client, patient_headers):
    body = {"full_name": "X", "date_of_birth": "2000-01-01"}
    assert client.post("/api/v1/patients", json=body).status_code == 401
    assert client.post("/api/v1/patients", json=body, headers=patient_headers).status_code == 403


# --- list / search ---


def test_list_includes_new_patient(client, staff_headers, patient):
    r = client.get("/api/v1/patients", headers=staff_headers)
    assert r.status_code == 200
    assert patient["id"] in {p["id"] for p in r.json()}


def test_search_by_name_case_insensitive(client, staff_headers, make_patient):
    tag = uuid.uuid4().hex[:10]
    target = make_patient(full_name=f"Zelda {tag} Example")
    make_patient()  # should not match
    r = client.get("/api/v1/patients", params={"q": tag.upper()}, headers=staff_headers)
    assert [p["id"] for p in r.json()] == [target["id"]]


def test_search_by_patient_code_lowercase(client, staff_headers, patient):
    r = client.get("/api/v1/patients", params={"q": patient["patient_code"].lower()}, headers=staff_headers)
    assert [p["id"] for p in r.json()] == [patient["id"]]


def test_search_treats_wildcards_literally(client, staff_headers, make_patient):
    tag = uuid.uuid4().hex[:8]
    literal = make_patient(full_name=f"Percent 100% {tag}")
    r = client.get("/api/v1/patients", params={"q": f"100% {tag}"}, headers=staff_headers)
    assert [p["id"] for p in r.json()] == [literal["id"]]
    r = client.get("/api/v1/patients", params={"q": "%"}, headers=staff_headers)
    assert all("%" in p["full_name"] or "%" in p["patient_code"] for p in r.json())
    r = client.get("/api/v1/patients", params={"q": "_"}, headers=staff_headers)
    assert all("_" in p["full_name"] or "_" in p["patient_code"] for p in r.json())


def test_search_no_match_returns_empty_list(client, staff_headers):
    r = client.get("/api/v1/patients", params={"q": f"nobody-{uuid.uuid4().hex}"}, headers=staff_headers)
    assert r.status_code == 200 and r.json() == []


def test_blank_search_returns_list(client, staff_headers, patient):
    r = client.get("/api/v1/patients", params={"q": "   "}, headers=staff_headers)
    assert patient["id"] in {p["id"] for p in r.json()}


def test_search_query_too_long(client, staff_headers):
    assert client.get("/api/v1/patients", params={"q": "x" * 101}, headers=staff_headers).status_code == 422


def test_list_is_newest_first(client, staff_headers, make_patient, db_session):
    tag = uuid.uuid4().hex[:8]
    older = make_patient(full_name=f"Order {tag} older")
    newer = make_patient(full_name=f"Order {tag} newer")
    # Inside one transaction now() is constant, so set distinct timestamps explicitly.
    now = datetime.now(timezone.utc)
    db_session.get(Patient, uuid.UUID(older["id"])).created_at = now - timedelta(days=1)
    db_session.get(Patient, uuid.UUID(newer["id"])).created_at = now
    db_session.commit()
    r = client.get("/api/v1/patients", params={"q": tag}, headers=staff_headers)
    assert [p["id"] for p in r.json()] == [newer["id"], older["id"]]


def test_list_requires_staff(client, patient_headers):
    assert client.get("/api/v1/patients").status_code == 401
    assert client.get("/api/v1/patients", headers=patient_headers).status_code == 403


# --- detail ---


def test_get_patient(client, staff_headers, patient):
    r = client.get(f"/api/v1/patients/{patient['id']}", headers=staff_headers)
    assert r.status_code == 200 and r.json() == patient


def test_get_unknown_patient_404(client, staff_headers):
    r = client.get(f"/api/v1/patients/{uuid.uuid4()}", headers=staff_headers)
    assert r.status_code == 404 and r.json() == {"detail": "Patient not found"}


def test_get_malformed_id_422(client, staff_headers):
    assert client.get("/api/v1/patients/not-a-uuid", headers=staff_headers).status_code == 422


def test_get_patient_requires_staff(client, patient, patient_headers):
    assert client.get(f"/api/v1/patients/{patient['id']}").status_code == 401
    assert client.get(f"/api/v1/patients/{patient['id']}", headers=patient_headers).status_code == 403
