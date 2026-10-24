import os

from dotenv import load_dotenv

load_dotenv()


def _database_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Copy backend/.env.example to backend/.env "
            "and paste your Neon connection string."
        )
    # Neon gives postgresql:// (or postgres://); SQLAlchemy needs the psycopg 3 driver name.
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


DATABASE_URL = _database_url()
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]


def _secret(name: str) -> str | None:
    # Treat unset or still-placeholder values as "not configured".
    v = os.getenv(name, "").strip()
    return None if not v or v.startswith("change-me") else v


SECRET_KEY = _secret("SECRET_KEY")
DEMO_STAFF_USERNAME = os.getenv("DEMO_STAFF_USERNAME", "staff").strip()
DEMO_STAFF_PASSWORD = _secret("DEMO_STAFF_PASSWORD")
TOKEN_MAX_AGE_SECONDS = 12 * 60 * 60
STAFF_DISPLAY_NAME = "Demo Staff"
