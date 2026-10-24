# MedVerify Backend (FastAPI + Neon)

> Prototype for demonstration only. Not for real clinical use. Synthetic data only.

API shapes for the frontend: see [`API_CONTRACT.md`](API_CONTRACT.md). Interactive docs: `{BASE_URL}/docs`.
Tests: `pip install -r requirements-dev.txt` then `python -m pytest`. See [`TESTING.md`](TESTING.md).

## Run locally (Windows PowerShell, from `backend/`)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # then fill in real values (never commit .env)
uvicorn app.main:app --reload
curl.exe http://127.0.0.1:8000/health   # expect {"status":"ok","database":"ok"}
```

Generate a `SECRET_KEY`:
`python -c "import secrets; print(secrets.token_urlsafe(32))"`

Tables are created automatically on startup (no migrations).

## Deploy to Render

New **Web Service** → connect the GitHub repo, then:

| Setting | Value |
|---|---|
| Root Directory | `backend` |
| Runtime | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |

Environment variables (Render dashboard → Environment):

| Name | Value |
|---|---|
| `PYTHON_VERSION` | `3.14.6` (version tested locally; use `3.13` if Render rejects it) |
| `DATABASE_URL` | Neon connection string |
| `SECRET_KEY` | long random string (different from local) |
| `DEMO_STAFF_USERNAME` | e.g. `staff` |
| `DEMO_STAFF_PASSWORD` | a strong demo password |
| `CORS_ORIGINS` | `http://localhost:5173,https://<your-app>.vercel.app` (exact origins, comma-separated, no trailing slash) |

After deploying, check `https://<service>.onrender.com/health` and `/docs`.
Free Render instances sleep when idle; the first request after a pause can take ~30–60 s.
