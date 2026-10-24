"""Demo-grade authentication. NOT production auth.

Tokens are signed (not encrypted) with SECRET_KEY and carry {"role", "sub"}.
Staff: a single demo account from env vars. Patient: patient_code + date_of_birth.
"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, TOKEN_MAX_AGE_SECONDS
from app.db import get_db
from app.models import Patient

_bearer = HTTPBearer(auto_error=False)


def _serializer() -> URLSafeTimedSerializer:
    if not SECRET_KEY:
        raise HTTPException(
            status_code=503, detail="Authentication is not configured on the server (SECRET_KEY)"
        )
    return URLSafeTimedSerializer(SECRET_KEY, salt="medverify-auth")


def create_token(role: str, sub: str) -> str:
    return _serializer().dumps({"role": role, "sub": sub})


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _claims(creds: HTTPAuthorizationCredentials | None) -> dict:
    if creds is None:
        raise _unauthorized("Not signed in")
    try:
        data = _serializer().loads(creds.credentials, max_age=TOKEN_MAX_AGE_SECONDS)
    except SignatureExpired:
        raise _unauthorized("Session expired, please sign in again")
    except BadSignature:
        raise _unauthorized("Invalid session token")
    if not isinstance(data, dict) or "role" not in data or "sub" not in data:
        raise _unauthorized("Invalid session token")
    return data


def require_staff(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> dict:
    claims = _claims(creds)
    if claims["role"] != "staff":
        raise HTTPException(status_code=403, detail="Staff access only")
    return claims


def require_patient(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Patient:
    claims = _claims(creds)
    if claims["role"] != "patient":
        raise HTTPException(status_code=403, detail="Patient access only")
    try:
        patient = db.get(Patient, uuid.UUID(claims["sub"]))
    except ValueError:
        patient = None
    if patient is None:
        raise _unauthorized("Invalid session token")
    return patient
