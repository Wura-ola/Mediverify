"""Official record entries: staff add visits; staff and patients read history."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models import RecordEntry


def _visits_url(patient):
    return f"/api/v1/patients/{patient['id']}/visits"


def _records_url(patient):
    return f"/api/v1/patients/{patient['id']}/records"


@pytest.fixture
def add_visit(client, staff_headers):
    def _add(patient, **body):
        payload = {"visit_date": "2026-10-20", "title": "Routine check-up", **body}
        r = client.post(_visits_url(patient), json=payload, headers=staff_headers)
        assert r.status_code == 201, r.text
        return r.json()

    return _add


def test_add_visit(client, staff_headers, patient):
    r = client.post(
        _visits_url(patient),
        json={"visit_date": "2026-10-20", "title": " Routine check-up ", "details": "Synthetic note."},
        headers=staff_headers,
    )
    assert r.status_code == 201
    e = r.json()
    assert set(e) == {
        "id", "patient_id", "visit_date", "record_type", "title", "details",
        "created_by", "source_external_record_id", "created_at",
    }
    assert e["patient_id"] == patient["id"]
    assert e["record_type"] == "visit_note"  # default
    assert e["title"] == "Routine check-up"
    assert e["details"] == "Synthetic note."
    assert e["created_by"] == "Demo Staff"
    assert e["source_external_record_id"] is None
    assert e["created_at"].endswith("Z")


@pytest.mark.parametrize("record_type", ["visit_note", "diagnosis", "prescription", "lab_result"])
def test_allowed_record_types(add_visit, patient, record_type):
    assert add_visit(patient, record_type=record_type)["record_type"] == record_type


def test_blank_details_become_null(add_visit, patient):
    assert add_visit(patient, details="   ")["details"] is None


@pytest.mark.parametrize(
    "body",
    [
        {"record_type": "external_import"},  # reserved for approved imports
        {"record_type": "surgery"},
        {"visit_date": "2999-01-01"},
        {"visit_date": "20/10/2026"},
        {"title": "  "},
        {"title": "x" * 201},
        {"details": "x" * 5001},
    ],
)
def test_add_visit_validation(client, staff_headers, patient, body):
    payload = {"visit_date": "2026-10-20", "title": "t", **body}
    assert client.post(_visits_url(patient), json=payload, headers=staff_headers).status_code == 422


def test_add_visit_missing_required_fields(client, staff_headers, patient):
    assert client.post(_visits_url(patient), json={"title": "t"}, headers=staff_headers).status_code == 422
    assert client.post(_visits_url(patient), json={"visit_date": "2026-10-20"}, headers=staff_headers).status_code == 422


def test_add_visit_unknown_patient(client, staff_headers):
    r = client.post(
        f"/api/v1/patients/{uuid.uuid4()}/visits", json={"visit_date": "2026-10-20", "title": "t"}, headers=staff_headers
    )
    assert r.status_code == 404


def test_add_visit_requires_staff(client, patient, patient_headers):
    payload = {"visit_date": "2026-10-20", "title": "t"}
    assert client.post(_visits_url(patient), json=payload).status_code == 401
    assert client.post(_visits_url(patient), json=payload, headers=patient_headers).status_code == 403


# --- staff reads history ---


def test_records_newest_visit_first(client, staff_headers, add_visit, patient):
    add_visit(patient, visit_date="2026-09-01", title="Oldest")
    add_visit(patient, visit_date="2026-10-22", title="Newest")
    add_visit(patient, visit_date="2026-10-20", title="Middle")
    r = client.get(_records_url(patient), headers=staff_headers)
    assert r.status_code == 200
    assert [e["title"] for e in r.json()] == ["Newest", "Middle", "Oldest"]


def test_records_same_day_ordered_by_creation(client, staff_headers, add_visit, patient, db_session):
    first = add_visit(patient, visit_date="2026-10-20", title="Earlier entry")
    second = add_visit(patient, visit_date="2026-10-20", title="Later entry")
    now = datetime.now(timezone.utc)
    db_session.get(RecordEntry, uuid.UUID(first["id"])).created_at = now - timedelta(hours=1)
    db_session.get(RecordEntry, uuid.UUID(second["id"])).created_at = now
    db_session.commit()
    titles = [e["title"] for e in client.get(_records_url(patient), headers=staff_headers).json()]
    assert titles == ["Later entry", "Earlier entry"]


def test_records_empty_for_new_patient(client, staff_headers, patient):
    assert client.get(_records_url(patient), headers=staff_headers).json() == []


def test_records_unknown_patient(client, staff_headers):
    assert client.get(f"/api/v1/patients/{uuid.uuid4()}/records", headers=staff_headers).status_code == 404


def test_records_require_staff(client, patient, patient_headers):
    assert client.get(_records_url(patient)).status_code == 401
    assert client.get(_records_url(patient), headers=patient_headers).status_code == 403


# --- patient's own view ---


def test_me_returns_own_profile(client, patient, patient_headers):
    r = client.get("/api/v1/patients/me", headers=patient_headers)
    assert r.status_code == 200 and r.json() == patient


def test_me_records_returns_own_history(client, add_visit, patient, patient_headers):
    entry = add_visit(patient, title="Mine")
    r = client.get("/api/v1/patients/me/records", headers=patient_headers)
    assert r.status_code == 200 and r.json() == [entry]


def test_patients_cannot_see_each_others_records(client, add_visit, make_patient, login_patient):
    ada, bola = make_patient(), make_patient()
    add_visit(ada, title="Ada only")
    bola_headers = login_patient(bola)
    assert client.get("/api/v1/patients/me/records", headers=bola_headers).json() == []
    assert client.get("/api/v1/patients/me", headers=bola_headers).json()["id"] == bola["id"]
    # And the staff URL for Ada's records is closed to Bola.
    assert client.get(_records_url(ada), headers=bola_headers).status_code == 403


def test_me_routes_require_patient(client, staff_headers):
    for url in ("/api/v1/patients/me", "/api/v1/patients/me/records"):
        assert client.get(url).status_code == 401
        assert client.get(url, headers=staff_headers).status_code == 403
