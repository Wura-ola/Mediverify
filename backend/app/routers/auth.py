import hmac

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import create_token
from app.config import DEMO_STAFF_PASSWORD, DEMO_STAFF_USERNAME
from app.db import get_db
from app.models import Patient
from app.schemas import PatientLogin, PatientToken, StaffLogin, StaffToken

router = APIRouter(prefix="/api/v1", tags=["auth (demo only)"])


@router.post("/staff/login", response_model=StaffToken)
def staff_login(body: StaffLogin):
    if not DEMO_STAFF_PASSWORD:
        raise HTTPException(status_code=503, detail="Demo staff login is not configured on the server")
    user_ok = hmac.compare_digest(body.username.encode(), DEMO_STAFF_USERNAME.encode())
    pass_ok = hmac.compare_digest(body.password.encode(), DEMO_STAFF_PASSWORD.encode())
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, detail="Username or password is incorrect")
    return StaffToken(access_token=create_token("staff", DEMO_STAFF_USERNAME))


@router.post("/patient/login", response_model=PatientToken)
def patient_login(body: PatientLogin, db: Session = Depends(get_db)):
    patient = db.scalar(select(Patient).where(Patient.patient_code == body.patient_code))
    # Same message for unknown code and wrong DOB, so codes can't be probed.
    if patient is None or patient.date_of_birth != body.date_of_birth:
        raise HTTPException(status_code=401, detail="Patient ID or date of birth is incorrect")
    return PatientToken(access_token=create_token("patient", str(patient.id)), patient=patient)
