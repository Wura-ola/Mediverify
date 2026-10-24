import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.db import Base, engine
from app import models  # noqa: F401  (registers tables for create_all)
from app.routers import auth, external_records, health, patients

log = logging.getLogger("medverify")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # No migrations for the hackathon: create any missing tables on startup.
    # If the DB is unreachable, still start so /health can report it.
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        log.error("Could not initialise database tables: %s", type(exc).__name__)
    yield


app = FastAPI(
    title="MedVerify API",
    description="Prototype for demonstration only. Not for real clinical use. Synthetic data only.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(external_records.patient_router)
app.include_router(external_records.staff_router)
app.include_router(patients.router)
