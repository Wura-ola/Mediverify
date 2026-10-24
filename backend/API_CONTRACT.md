# MedVerify API Contract (v1, draft)

> Prototype for demonstration only. Not for real clinical use. Synthetic data only.
> Status column shows what is **implemented and tested** on the backend. Everything else is the agreed
> shape the frontend can mock against now; it will not change without telling the frontend developer.

## Basics

- **Base URL:** `VITE_API_BASE_URL` (local: `http://127.0.0.1:8000`, production: Render URL, shared once deployed).
- **Interactive docs:** `{BASE_URL}/docs`
- **Format:** JSON, except file upload (`multipart/form-data`) and file download (binary).
- **Dates:** `YYYY-MM-DD`. **Timestamps:** ISO 8601 UTC, e.g. `2026-10-24T10:15:00Z`.
- **IDs:** `id` fields are UUID strings. `patient_code` is the human-facing Patient ID, format `MV-XXXXXXXX`.
- **Auth (demo-grade, not production):** login returns `access_token`; send it as
  `Authorization: Bearer <access_token>`. Tokens expire after 12 hours.
- **Errors:** always `{"detail": "<message>"}` (validation errors: `detail` is a list, FastAPI default).
  `401` not signed in / bad token · `403` wrong role · `404` not found · `413` file too large ·
  `415` file type not allowed · `422` invalid input · `503` database unavailable.

## Endpoints

| Status | Method | Path | Auth |
|---|---|---|---|
| ⏳ | GET | `/health` | public |
| ⏳ | POST | `/api/v1/staff/login` | public |
| ⏳ | POST | `/api/v1/patient/login` | public |
| ⏳ | POST | `/api/v1/patients` | staff |
| ⏳ | GET | `/api/v1/patients?q=` | staff |
| ⏳ | GET | `/api/v1/patients/{id}` | staff |
| ⏳ | POST | `/api/v1/patients/{id}/visits` | staff |
| ⏳ | GET | `/api/v1/patients/{id}/records` | staff |
| ⏳ | GET | `/api/v1/patients/me` | patient |
| ⏳ | GET | `/api/v1/patients/me/records` | patient |
| ⏳ | POST | `/api/v1/patients/me/external-records` | patient |
| ⏳ | GET | `/api/v1/patients/me/external-records` | patient |
| ⏳ | GET | `/api/v1/patients/me/external-records/{id}/file` | patient |
| ⏳ | GET | `/api/v1/staff/external-records?status=pending_review` | staff |
| ⏳ | GET | `/api/v1/staff/external-records/{id}` | staff |
| ⏳ | GET | `/api/v1/staff/external-records/{id}/file` | staff |
| ⏳ | POST | `/api/v1/staff/external-records/{id}/approve` | staff |
| ⏳ | POST | `/api/v1/staff/external-records/{id}/reject` | staff |

✅ = implemented and tested · ⏳ = agreed shape, not built yet

---

### GET `/health`
`200` → `{"status": "ok", "database": "ok"}`
`503` → `{"status": "degraded", "database": "unavailable"}`

### POST `/api/v1/staff/login`
Request: `{"username": "staff", "password": "..."}` (demo credentials shared out-of-band, never in git)
`200` → `{"access_token": "<token>", "token_type": "bearer", "role": "staff", "display_name": "Demo Staff"}`
`401` → wrong credentials

### POST `/api/v1/patient/login`
Request: `{"patient_code": "MV-7K3QH9TZ", "date_of_birth": "2002-04-15"}`
`200` → `{"access_token": "<token>", "token_type": "bearer", "role": "patient", "patient": <Patient>}`
`401` → `{"detail": "Patient ID or date of birth is incorrect"}` (same message for both, by design)

### Patient object
```json
{
  "id": "6f1c...-uuid",
  "patient_code": "MV-7K3QH9TZ",
  "full_name": "Ada Example",
  "date_of_birth": "2002-04-15",
  "sex_or_gender": "Female",
  "phone": "08000000000",
  "created_at": "2026-10-24T10:15:00Z"
}
```
`sex_or_gender` and `phone` may be `null`.

### POST `/api/v1/patients` (staff)
Request: `{"full_name": "Ada Example", "date_of_birth": "2002-04-15", "sex_or_gender": "Female", "phone": "08000000000"}`
- `full_name` (required, 1–200 chars), `date_of_birth` (required, not in the future), others optional.

`201` → `<Patient>` (includes the new `patient_code`, so show it to staff prominently)

### GET `/api/v1/patients?q=ada` (staff)
`q` is optional and matches part of the name or Patient ID, case-insensitive. Newest first, max 100.
`200` → `[<Patient>, ...]` (empty list when there are no matches)

### GET `/api/v1/patients/{id}` (staff)
`200` → `<Patient>` · `404` if unknown

### RecordEntry object (official record)
```json
{
  "id": "uuid",
  "patient_id": "uuid",
  "visit_date": "2026-10-20",
  "record_type": "visit_note",
  "title": "Routine check-up",
  "details": "Synthetic note: patient reports mild headache.",
  "created_by": "Demo Staff",
  "source_external_record_id": null,
  "created_at": "2026-10-24T10:20:00Z"
}
```
`record_type` is one of `visit_note`, `diagnosis`, `prescription`, `lab_result`, `external_import`.
`source_external_record_id` is set only on entries created by approving an external record.

### POST `/api/v1/patients/{id}/visits` (staff)
Request: `{"visit_date": "2026-10-20", "record_type": "visit_note", "title": "Routine check-up", "details": "..."}`
- `visit_date` and `title` required. `record_type` defaults to `visit_note`. `details` optional (max 5000 chars).

`201` → `<RecordEntry>` · `404` unknown patient

### GET `/api/v1/patients/{id}/records` (staff) and GET `/api/v1/patients/me/records` (patient)
`200` → `[<RecordEntry>, ...]` newest `visit_date` first. **Official entries only**: pending or rejected
external records never appear here.

### GET `/api/v1/patients/me` (patient)
`200` → `<Patient>` for the signed-in patient. A patient can never request another patient's data.

### ExternalRecord object
```json
{
  "id": "uuid",
  "patient_id": "uuid",
  "patient_code": "MV-7K3QH9TZ",
  "patient_name": "Ada Example",
  "original_filename": "old_lab_report.jpg",
  "content_type": "image/jpeg",
  "size_bytes": 182344,
  "source_facility": "Sample General Hospital",
  "document_date": "2024-03-02",
  "document_type": "lab_result",
  "notes": "Patient-entered summary of the document.",
  "extraction_status": "not_available",
  "review_status": "pending_review",
  "review_note": null,
  "reviewed_by": null,
  "reviewed_at": null,
  "uploaded_at": "2026-10-24T11:00:00Z"
}
```
- `extraction_status`: always `not_available` in the MVP (no OCR). The UI should say
  "Automatic extraction not available. Fields below were entered by the patient."
- `review_status`: `pending_review` | `approved` | `rejected`.
- The file itself is never in this JSON; fetch it from the `/file` endpoint.

### POST `/api/v1/patients/me/external-records` (patient, multipart/form-data)
Fields: `file` (required; PDF, PNG or JPEG; max 5 MB), and the optional text fields `source_facility`, `document_date`
(`YYYY-MM-DD`), `document_type`, `notes`.
`201` → `<ExternalRecord>` with `review_status: "pending_review"` · `413` too large · `415` wrong type

### GET `/api/v1/patients/me/external-records` (patient)
`200` → `[<ExternalRecord>, ...]` newest first (only the signed-in patient's own uploads)

### GET `.../external-records/{id}/file` (patient: own only; staff: any)
`200` → the original file bytes with the correct `Content-Type` (use as `<img src>` / `<iframe>` via a
blob URL, because the request needs the Authorization header).

### GET `/api/v1/staff/external-records?status=pending_review` (staff)
`status` is optional (omit it for all). `200` → `[<ExternalRecord>, ...]` newest first.

### GET `/api/v1/staff/external-records/{id}` (staff)
`200` → `<ExternalRecord>`

### POST `/api/v1/staff/external-records/{id}/approve` and `/reject` (staff)
Request: `{"review_note": "optional text"}`
`200` → updated `<ExternalRecord>`. Approve also creates one official `RecordEntry`
(`record_type: "external_import"`, linked through `source_external_record_id`).
`409` if the item has already been reviewed.
