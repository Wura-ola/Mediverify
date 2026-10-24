"""Demo login endpoints and token / role enforcement."""

import uuid

import pytest
from itsdangerous import URLSafeTimedSerializer

from app import auth
from app.routers import auth as auth_routes

from .conftest import STAFF_PASSWORD, STAFF_USERNAME

STAFF_ONLY_URL = "/api/v1/patients"
PATIENT_ONLY_URL = "/api/v1/patients/me"


def _bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# --- staff login ---


def test_staff_login_success(client):
    r = client.post("/api/v1/staff/login", json={"username": STAFF_USERNAME, "password": STAFF_PASSWORD})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer" and body["role"] == "staff"
    assert body["display_name"] == "Demo Staff" and body["access_token"]


@pytest.mark.parametrize(
    "username, password",
    [(STAFF_USERNAME, "wrong"), ("someone", STAFF_PASSWORD), (STAFF_USERNAME.upper(), STAFF_PASSWORD)],
)
def test_staff_login_wrong_credentials(client, username, password):
    r = client.post("/api/v1/staff/login", json={"username": username, "password": password})
    assert r.status_code == 401
    assert r.json() == {"detail": "Username or password is incorrect"}


@pytest.mark.parametrize("body", [{}, {"username": "x"}, {"username": "", "password": ""}])
def test_staff_login_validation(client, body):
    assert client.post("/api/v1/staff/login", json=body).status_code == 422


def test_staff_login_not_configured(client, monkeypatch):
    monkeypatch.setattr(auth_routes, "DEMO_STAFF_PASSWORD", None)
    r = client.post("/api/v1/staff/login", json={"username": STAFF_USERNAME, "password": STAFF_PASSWORD})
    assert r.status_code == 503


def test_login_refused_without_secret_key(client, monkeypatch):
    monkeypatch.setattr(auth, "SECRET_KEY", None)
    r = client.post("/api/v1/staff/login", json={"username": STAFF_USERNAME, "password": STAFF_PASSWORD})
    assert r.status_code == 503
    assert "SECRET_KEY" in r.json()["detail"]


# --- patient login ---


def test_patient_login_success(client, patient):
    r = client.post(
        "/api/v1/patient/login",
        json={"patient_code": patient["patient_code"], "date_of_birth": patient["date_of_birth"]},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["role"] == "patient" and body["access_token"]
    assert body["patient"]["id"] == patient["id"]


def test_patient_login_accepts_lowercase_padded_code(client, patient):
    r = client.post(
        "/api/v1/patient/login",
        json={"patient_code": f"  {patient['patient_code'].lower()} ", "date_of_birth": patient["date_of_birth"]},
    )
    assert r.status_code == 200


def test_patient_login_same_error_for_wrong_dob_and_unknown_code(client, patient):
    wrong_dob = client.post(
        "/api/v1/patient/login", json={"patient_code": patient["patient_code"], "date_of_birth": "1901-01-01"}
    )
    unknown = client.post(
        "/api/v1/patient/login", json={"patient_code": "MV-ZZZZZZZZ", "date_of_birth": patient["date_of_birth"]}
    )
    assert wrong_dob.status_code == unknown.status_code == 401
    assert wrong_dob.json() == unknown.json() == {"detail": "Patient ID or date of birth is incorrect"}


@pytest.mark.parametrize(
    "body",
    [{}, {"patient_code": "MV-AAAAAAAA"}, {"patient_code": "MV-AAAAAAAA", "date_of_birth": "15/04/2002"}],
)
def test_patient_login_validation(client, body):
    assert client.post("/api/v1/patient/login", json=body).status_code == 422


# --- token checks ---


def test_missing_token_is_401_with_bearer_challenge(client):
    r = client.get(STAFF_ONLY_URL)
    assert r.status_code == 401
    assert r.json() == {"detail": "Not signed in"}
    assert r.headers.get("www-authenticate") == "Bearer"


@pytest.mark.parametrize("header", ["Bearer not-a-real-token", "Bearer ", "Basic abc"])
def test_garbage_or_wrong_scheme_token_is_401(client, header):
    assert client.get(STAFF_ONLY_URL, headers={"Authorization": header}).status_code == 401


def test_token_signed_with_other_key_is_rejected(client):
    forged = URLSafeTimedSerializer("attacker-key", salt="medverify-auth").dumps({"role": "staff", "sub": "x"})
    r = client.get(STAFF_ONLY_URL, headers=_bearer(forged))
    assert r.status_code == 401 and r.json()["detail"] == "Invalid session token"


def test_expired_token_is_rejected(client, staff_headers, monkeypatch):
    monkeypatch.setattr(auth, "TOKEN_MAX_AGE_SECONDS", -1)
    r = client.get(STAFF_ONLY_URL, headers=staff_headers)
    assert r.status_code == 401 and "expired" in r.json()["detail"].lower()


@pytest.mark.parametrize("payload", [["staff"], {"role": "staff"}, {"sub": "x"}, "staff"])
def test_validly_signed_but_malformed_payload_is_rejected(client, payload):
    token = auth._serializer().dumps(payload)
    assert client.get(STAFF_ONLY_URL, headers=_bearer(token)).status_code == 401


@pytest.mark.parametrize("sub", [str(uuid.uuid4()), "not-a-uuid"])
def test_patient_token_for_missing_patient_is_rejected(client, sub):
    token = auth.create_token("patient", sub)
    assert client.get(PATIENT_ONLY_URL, headers=_bearer(token)).status_code == 401


def test_unknown_role_is_forbidden(client):
    token = auth.create_token("admin", "x")
    assert client.get(STAFF_ONLY_URL, headers=_bearer(token)).status_code == 403
    assert client.get(PATIENT_ONLY_URL, headers=_bearer(token)).status_code == 403


def test_patient_token_cannot_use_staff_routes(client, patient_headers):
    r = client.get(STAFF_ONLY_URL, headers=patient_headers)
    assert r.status_code == 403 and r.json() == {"detail": "Staff access only"}


def test_staff_token_cannot_use_patient_routes(client, staff_headers):
    r = client.get(PATIENT_ONLY_URL, headers=staff_headers)
    assert r.status_code == 403 and r.json() == {"detail": "Patient access only"}
