# MedVerify Backend: Tests

170 automated tests covering every endpoint in [`API_CONTRACT.md`](API_CONTRACT.md), plus the
helpers, config and validation rules behind them. Tests use synthetic data only.

## Running the tests

From `backend/`, with the virtual environment active:

```powershell
pip install -r requirements-dev.txt     # once: adds pytest + httpx
python -m pytest                        # whole suite (about 7 minutes against Neon)
python -m pytest tests/test_unit.py     # fast, no HTTP (seconds)
python -m pytest tests/test_auth.py -v  # one file, list each test
python -m pytest -k approve             # tests whose name matches "approve"
python -m pytest -x                     # stop at the first failure
```

Expected result: `170 passed`. One warning, `StarletteDeprecationWarning: Using httpx ...`,
comes from the test client library and is harmless.

### What the tests need

- **`DATABASE_URL`** (from `.env`) or **`TEST_DATABASE_URL`**. The tests run against real PostgreSQL.
- Nothing else. The tests set their own `SECRET_KEY` and demo staff login *before* the app loads,
  so the real secrets in `.env` are never used and don't need to be set. Use made-up values in
  `tests/conftest.py`, never real ones: this repository is public.

## Why it's safe to run against the shared Neon database

Every test runs inside a database transaction that is **rolled back** when the test ends.
The app still calls `commit()`, but in tests that only releases a savepoint inside the outer
transaction (`join_transaction_mode="create_savepoint"`), so **nothing is ever saved**. The demo
data (for example Ada) is untouched, and the live site never sees test patients.

`test_health.py::test_isolation_step1_create` / `step2_nothing_was_committed` prove this on
every run: step 1 creates a patient, and step 2 checks from a fresh connection that it doesn't exist.

The only thing the suite writes for real is `CREATE TABLE IF NOT EXISTS` (the same thing app
startup does).

**Optional, more isolated:** create a Neon *branch* (Neon dashboard → Branches → Create) and run:

```powershell
$env:TEST_DATABASE_URL = "postgresql://...branch-connection-string..."
python -m pytest
```

## What is covered

| File | Tests | Covers |
|---|---|---|
| `test_unit.py` | 45 | `DATABASE_URL` rewrite and missing-URL error · placeholder secrets treated as unset · Patient ID format, alphabet and randomness · file-type detection by signature · filename sanitising · document date parsing · text length limits · every Pydantic schema rule · UTC `Z` timestamps |
| `test_health.py` | 9 | `/health` OK and 503 without leaking connection details · `/docs` and all 18 routes registered · CORS allowed / preflight / blocked origin · unknown route 404 · **rollback isolation proof** |
| `test_auth.py` | 30 | Staff login success / wrong user / wrong password / 422 / 503 when not configured · 503 without `SECRET_KEY` · patient login, forgiving Patient ID input, **same error for wrong DOB and unknown ID** · missing / garbage / wrong-scheme / forged / expired / malformed tokens · token for a deleted patient · unknown role · staff vs patient role separation |
| `test_patients.py` | 20 | Register (shape, trimming, blanks → null, validation) · unique Patient IDs · **retry on Patient ID collision, and give up with 500** · list, search by name / Patient ID, case-insensitive, `%` and `_` treated literally, no match, long query · newest first · detail 200/404/422 · staff-only everywhere |
| `test_records.py` | 25 | Add visit (shape, default type, every allowed type, `external_import` reserved, date/title/details rules) · unknown patient 404 · history newest-first and same-day tie-break · `/me` and `/me/records` · **patients can't see each other's records** · staff-only and patient-only enforcement |
| `test_external_records.py` | 41 | Upload (full shape, `pending_review`, `extraction_status: not_available`) · type taken from file contents, not the label · sanitised filename · 415 / 413 / exactly-5 MB accepted / empty / missing file / field rules · own-list and own-file only (**404 for another patient's file**) · download headers (`nosniff`, `no-store`) · staff list, filter, detail, file · **pending/rejected never in the official record** · approve creates one linked `external_import` entry (date and title fallbacks) · reject · **no second review (409), all 4 combinations** · auth on all 8 routes |

### Checking that the tests can fail

A test suite that always passes proves nothing, so three real bugs were introduced on purpose and
each one was caught:

| Bug introduced | Caught by |
|---|---|
| Removed the staff check from `GET /api/v1/patients` | 3 auth/patient tests failed |
| Removed the "already reviewed" check | 4 `test_cannot_review_twice` cases failed |
| Patient history ignored which patient it belonged to | 2 record isolation tests failed |

## Not covered by this suite (and why)

| Area | Status |
|---|---|
| Two staff approving the **same upload at the same moment** | The row lock needs two real concurrent transactions, which the rollback design can't express. Verified manually against Neon: 3 simultaneous approvals gave one 200, two 409s and exactly one official entry. |
| Token expiry after a real 12 hours | Tested by setting the max age below zero; the 12-hour value itself isn't waited out. |
| The deployed Render service | Checked by hand with live calls after each deploy (see the commit history). This suite tests the code, not the hosting. |
| Frontend | Out of scope (separate developer). |

## Adding a test

Use the fixtures in `tests/conftest.py`:

| Fixture | Gives you |
|---|---|
| `client` | `TestClient` wired to a rolled-back DB session |
| `staff_headers` | `Authorization` header for the demo staff user |
| `make_patient(...)` | registers a synthetic patient (unique name), returns its JSON |
| `patient`, `patient_headers` | one ready-made patient and their login header |
| `login_patient(p)` | login header for any patient JSON |
| `db_session` | the same session the app uses, to set fields directly |
| `PNG_BYTES`, `PDF_BYTES`, `JPEG_BYTES`, `HTML_BYTES` | tiny synthetic files |

Inside a test, PostgreSQL's `now()` returns the same time for every row (it's one transaction).
To test "newest first" ordering, set `created_at` / `uploaded_at` explicitly through
`db_session`, as `test_list_is_newest_first` does.
