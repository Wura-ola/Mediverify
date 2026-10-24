# MedVerify — Product Requirements & Build Brief

**Document purpose:** Give Claude Code a single source of truth for building the MedVerify hackathon prototype.

**Product type:** Hospital medical-record management and patient record portability prototype  
**Primary users:** Hospital staff and patients  
**Target demo:** A working end-to-end flow that can be demonstrated from a live URL  
**Suggested stack:** React + Tailwind CSS frontend; Python + FastAPI backend; PostgreSQL hosted on Neon; backend deployed to Render; frontend deployed to Vercel; GitHub for collaboration.

---

## 1. Product Summary

MedVerify helps a hospital create and manage a patient's official medical record while allowing the patient to access and carry a copy of their records when visiting another hospital.

When a patient has a paper record or document from a hospital that does not use MedVerify, the patient can upload a photo or file. MedVerify preserves the original document and can extract information into structured fields. The extracted information remains **external and pending review** until authorized hospital staff review it. Patient-uploaded information must never silently become part of the official hospital record.

MedVerify is a record-management and portability prototype. It is **not** a diagnostic system, does not recommend treatment, and does not independently certify that a medical document or its contents are authentic.

## 2. Problem Being Solved

Medical information can be scattered across hospitals, paper documents, lab reports, and prescriptions. When patients visit a different hospital, they may not have an easy way to carry or present their previous medical history. Paper documents may also be difficult to read or organize.

MedVerify demonstrates a simple bridge between these situations:

1. A participating hospital creates and maintains a patient's official MedVerify record.
2. The patient can securely view and download available records.
3. The patient can upload a record from a non-participating hospital.
4. MedVerify keeps the original file and organizes any extracted information for review.
5. Authorized hospital staff can review the external information before deciding whether to add it to the official record.

## 3. Product Principles

- **Hospital-managed official record:** Hospital staff create and update official clinical entries.
- **Patient access, not patient editing:** Patients may view and download their records and submit external documents, but cannot directly edit official diagnoses, prescriptions, visits, or lab results.
- **Source transparency:** Every external item must show where it came from, when it was uploaded, and its review status when known.
- **Original preservation:** Keep the uploaded source document associated with the extracted fields. Do not replace the original with extracted text.
- **Review before inclusion:** Extracted external information is not an official record until authorized staff explicitly review and approve it.
- **Privacy by default:** Use synthetic demo data only. Do not put real patient data, secrets, database credentials, or tokens in source control.
- **No unsupported clinical claims:** Do not infer a diagnosis, prescribe treatment, or invent missing information during extraction.
- **Prototype-first:** Build a narrow, reliable end-to-end workflow before adding optional features.

## 4. User Roles and Permissions

### 4.1 Hospital staff

Hospital staff are the authorized creators and managers of official records. For the prototype, a single staff role is sufficient; do not build a complex role hierarchy unless the core workflow is already working.

Staff can:
- Register a patient.
- Generate a unique Patient ID.
- View a patient's profile and history.
- Add a visit and a diagnosis/note.
- Add prescription and lab-result entries.
- View external documents submitted by patients.
- Review extracted information and approve or reject it for inclusion in the official record.
- Download or print a patient's record summary.

### 4.2 Patient

Patients can:
- Sign in using Patient ID plus the configured identity check for the prototype.
- View their own patient profile and official medical history.
- View recent visits and individual record entries.
- Download or print a record summary.
- Upload a photo or file containing an external medical document.
- View extracted fields and the source document where supported.
- Submit the extracted information for hospital review.
- See whether a submission is pending, approved, or rejected.

Patients cannot:
- Register themselves as official patients.
- Change official medical history, diagnoses, prescriptions, or lab results.
- Approve their own imported documents.
- View another patient's information.

### Important authentication note

Patient ID alone is not a secure authentication factor. For a demo, use Patient ID plus a second identity field (for example, date of birth) only with synthetic test patients and clearly treat it as a simplified demonstration. Do not describe that mechanism as production-grade authentication. A real deployment would require stronger identity verification, secure session handling, audit logging, access controls, and a privacy/security review.

## 5. Core User Journeys

### Journey A — Hospital registers a patient

1. Staff opens the staff dashboard.
2. Staff enters the patient's basic details.
3. Backend generates a unique, non-sequential Patient ID.
4. Backend saves the patient to PostgreSQL.
5. UI displays the new Patient ID clearly so it can be shared with the patient.
6. Staff can open that patient's profile.

**Success condition:** The patient persists after refreshing the page, and the Patient ID is unique.

### Journey B — Hospital adds a visit

1. Staff opens a patient profile.
2. Staff chooses “Add visit”.
3. Staff enters the visit date, clinical note/diagnosis, and optional prescription/lab-result details.
4. Backend validates and stores the entry linked to the correct patient.
5. The entry appears in the patient's history, newest first.

**Success condition:** A visit saved by staff appears in the record history and can be retrieved from the API.

### Journey C — Patient views and downloads records

1. Patient opens the patient portal.
2. Patient signs in using Patient ID and the configured demo identity check.
3. Backend returns only that patient's permitted record data.
4. Patient views profile details, recent visits, and individual entries.
5. Patient selects “Download/Print record”.
6. The frontend produces a readable print view; browser print-to-PDF is acceptable for the prototype.

**Success condition:** Patient can view and print their own record without being able to edit official entries or access another patient.

### Journey D — Patient imports an external record

1. Patient chooses “Import external record”.
2. Patient uploads a supported image or PDF.
3. Backend checks file type and size, stores the original file safely, and associates it with the authenticated patient.
4. The prototype extracts a limited set of fields if a usable OCR tool is available. If OCR is not available or fails, show an honest “Could not extract automatically” state and allow a clearly labelled manual confirmation/edit of the extracted draft.
5. Show extracted fields such as document date, facility/source name, document type, and visible text/notes where available.
6. Patient submits the draft for review.
7. Status becomes `pending_review`.
8. Hospital staff sees the source document, extracted draft, uploader, and status.
9. Staff reviews and either approves or rejects it, optionally adding a review note.
10. Only approved information can be copied into the official record. Preserve the association to the original source and record the reviewer and review time where feasible.

**Success condition:** An imported item is visibly separate from official records until a staff member approves it.

### Journey E — Patient visits a non-participating hospital

The patient signs in to MedVerify and downloads or prints their current record summary to present elsewhere. This is a record-portability demonstration; the other hospital does not need to use MedVerify to read a printed or downloaded copy.

## 6. MVP Scope for a Short Hackathon

### P0 — Must work in the live demo

1. Staff demo login or a clearly labelled seeded staff demo session.
2. Register patient and generate Patient ID.
3. Patient list/search and patient detail/history.
4. Add a visit/note to a patient.
5. Patient sign-in and read-only view of their own records.
6. Download/print-friendly patient record summary.
7. Upload an external document and create a pending-review item.
8. Staff can open the pending item and approve/reject it.
9. Frontend and backend work together against the deployed API.
10. Backend health endpoint and working database connection.

### P1 — Implement only after P0 works

- Structured prescription entry.
- Structured lab-result entry.
- OCR extraction from uploaded images/PDFs.
- Search/filter by date or record type.
- Basic audit fields for record creation and external-record review.

### Out of scope for the initial prototype

- AI diagnosis or treatment recommendations.
- Automated clinical decision-making.
- Hospital billing, inventory, appointments, insurance, or pharmacy management.
- Integrations with national health systems or other hospitals.
- Production-grade identity verification or regulatory compliance claims.
- Complex multi-hospital administration, advanced permissions, or elaborate analytics.

If time is very short, finish P0 items 1–6 before adding OCR. A clear upload-and-review flow with an honest extraction status is better than a fragile “AI OCR” feature that pretends to work.

## 7. Suggested Screens

### Shared
- Landing page with a short explanation and separate “Hospital Staff” and “Patient Portal” entry points.
- Clear loading, empty, success, and error states.

### Hospital side
- Staff login/demo entry.
- Dashboard with patient search/list and pending external-record count.
- Register-patient form.
- Patient details page with profile, history, and “Add visit” form.
- External-record review screen showing the original document, extracted fields, source, upload time, and Approve/Reject actions.

### Patient side
- Patient login.
- Patient overview with Patient ID and recent visits.
- Medical history/record detail.
- Import external record page with upload, extraction status, editable draft fields, and review status.
- Print-friendly record view.

Use a clean, accessible healthcare-product interface. Prioritize readable typography, clear status labels, responsive layouts, and obvious actions. Do not spend MVP time on decorative animations.

## 8. Technical Architecture

### Frontend
- React and Tailwind CSS.
- All backend calls must go through the API; never connect the browser directly to PostgreSQL.
- Store the backend base URL in an environment variable such as `VITE_API_BASE_URL`.
- During local development, point it to the local API; in production, point it to the deployed backend URL.
- Keep API request code in one small service/helper module rather than scattering hard-coded URLs throughout components.
- Do not commit private keys or secrets into frontend environment variables. Anything bundled into a browser app should be treated as public.

### Backend
- Python and FastAPI.
- Pydantic request/response validation.
- PostgreSQL on Neon.
- Use SQLAlchemy or another existing ORM if already present in the repository. Do not replace a working project structure without a reason.
- Keep routes, schemas, database setup, and business logic reasonably separated, but avoid unnecessary abstraction for a short prototype.
- Expose interactive API documentation at `/docs`.
- Include `/health` and make its response clear about application status. If practical, include a safe database-connectivity check without exposing secrets.

### Deployment
- Frontend: Vercel.
- Backend: Render.
- Database: Neon PostgreSQL.
- Repository: GitHub; both developers should work from the same repository with agreed folder ownership.
- Configure the backend database connection using a Render environment variable such as `DATABASE_URL`.
- Configure frontend `VITE_API_BASE_URL` to the deployed backend URL.
- Configure FastAPI CORS to allow the exact local frontend origin used for development and the deployed Vercel origin. Do not use unrestricted CORS as a permanent solution.
- Ensure database migrations or table initialization are applied in the deployed environment.
- Never commit `.env` files, credentials, API keys, private uploads, or real patient records.

### Suggested repository layout

Use the current repository structure if one already exists. Otherwise, a simple layout is enough:

```text
medverify/
  frontend/          # React + Tailwind
  backend/           # FastAPI application
  README.md
  .gitignore
  .env.example       # Names of required variables; no real values
```

## 9. Proposed Data Model

Keep the schema minimal and consistent. Adapt names to the existing project where practical.

### Patient
- `id`: internal UUID primary key.
- `patient_code`: unique, human-readable Patient ID generated by the backend.
- `full_name`.
- `date_of_birth`: optional for the demo identity check.
- `sex_or_gender`: optional, only if required by the demo.
- `phone`: optional and use synthetic values only.
- `created_at`.

### StaffUser
- `id`.
- `display_name`.
- `email` or username.
- Password hash if password authentication is implemented; never store plain-text passwords.
- `created_at`.

### Visit / MedicalRecordEntry
- `id`.
- `patient_id` foreign key.
- `visit_date`.
- `record_type` such as `visit_note`, `diagnosis`, `prescription`, or `lab_result`.
- `title` or summary.
- `details` / structured JSON for the prototype where appropriate.
- `created_by_staff_id` when available.
- `created_at`.
- Optional `source_external_record_id` to preserve provenance for entries originating from an approved import.

### ExternalRecord
- `id`.
- `patient_id` foreign key.
- `original_filename` (sanitized for display; do not trust the raw filename as a storage path).
- `storage_key` or safe file location reference.
- `content_type` and file size.
- `source_facility` and `document_date` when known.
- `extracted_text` and/or `extracted_fields` as a draft.
- `review_status`: `pending_review`, `approved`, or `rejected`.
- `reviewed_by_staff_id`, `reviewed_at`, and `review_note` where feasible.
- `uploaded_at`.

Do not conflate an external-record upload with an official medical record entry. Keep the source document and the review decision linked.

## 10. Suggested API Contract

Use `/api/v1` as the versioned API prefix. The exact routes may be adapted to existing code, but the frontend developer and backend developer must agree on the final request and response shapes before integration.

| Method | Suggested endpoint | Purpose | Access |
|---|---|---|---|
| `GET` | `/health` | Application status | Public, no sensitive details |
| `POST` | `/api/v1/staff/login` | Staff sign-in or demo session | Staff |
| `POST` | `/api/v1/patients` | Register patient and generate Patient ID | Staff |
| `GET` | `/api/v1/patients` | List/search patients | Staff |
| `GET` | `/api/v1/patients/{patient_id}` | Patient profile | Authorized staff / that patient |
| `GET` | `/api/v1/patients/{patient_id}/records` | Official record history | Authorized staff / that patient |
| `POST` | `/api/v1/patients/{patient_id}/visits` | Add visit or official entry | Staff |
| `POST` | `/api/v1/patient/login` | Patient sign-in | Patient |
| `POST` | `/api/v1/patients/me/external-records` | Upload an external document | That patient |
| `GET` | `/api/v1/patients/me/external-records` | List patient's imports and statuses | That patient |
| `GET` | `/api/v1/staff/external-records?status=pending_review` | List submissions for review | Staff |
| `GET` | `/api/v1/staff/external-records/{id}` | View source and extraction draft | Staff |
| `POST` | `/api/v1/staff/external-records/{id}/approve` | Approve reviewed information | Staff |
| `POST` | `/api/v1/staff/external-records/{id}/reject` | Reject submission | Staff |

For a time-limited demo, avoid implementing every optional route if it prevents core flows from working. However, names and payloads must be documented and stable before the frontend integration begins.

### Example patient registration request

```json
{
  "full_name": "Ada Example",
  "date_of_birth": "2002-04-15",
  "sex_or_gender": "Female",
  "phone": "08000000000"
}
```

### Example successful registration response

```json
{
  "id": "<uuid>",
  "patient_code": "MV-<unique-code>",
  "full_name": "Ada Example",
  "created_at": "<ISO-8601 timestamp>"
}
```

These are illustrative shapes, not credentials or real patient data. Use synthetic information in demos.

### API conventions

- Return appropriate HTTP status codes and predictable JSON responses.
- Validate required fields and return actionable error messages.
- Use `201 Created` when creating a resource, `200 OK` for successful reads/updates, `400` or `422` for invalid input, `401` for unauthenticated requests, `403` for access denied, and `404` when a resource does not exist or cannot be disclosed.
- Keep date and timestamp formats consistent (ISO 8601).
- Never send database credentials, stack traces, or secrets in API responses.
- Make the frontend's handling of loading, success, and error states explicit.

## 11. Frontend–Backend Collaboration Contract

The frontend and backend developers are working on separate laptops. They should agree on these points early:

1. **Repository ownership:** Use one GitHub repository. Agree on folder ownership and avoid editing the same files concurrently. For example, one developer owns `frontend/`, the other owns `backend/`.
2. **Endpoint contract:** Agree on route, HTTP method, input JSON, output JSON, and expected errors for each screen.
3. **Mock first:** The frontend can use clearly labelled mock data while the backend endpoints are being built. Replace mock calls with real API calls once the backend is reachable.
4. **Local integration:** The frontend calls the backend's local URL while both are developing on their own laptops only if that backend is running on the same laptop. For cross-laptop testing, use a shared development deployment or deploy the backend and provide its URL. Do not assume `localhost` on one laptop refers to the other laptop.
5. **CORS:** Allow the frontend's origin in FastAPI so browser requests are accepted.
6. **Environment configuration:** Each developer maintains local environment variables. Share variable names and setup instructions, never secret values in chat or commits.
7. **Integration test:** Register a synthetic patient in the staff UI, add a visit, sign in as that patient, and verify the visit appears in the patient portal.
8. **Final live test:** Use the deployed Vercel URL on a separate browser/session. Confirm that the deployed frontend calls the deployed backend and that saved data persists after refresh.

## 12. File Upload and External-Document Safety

For the prototype:
- Allow only defined file types (for example PDF, PNG, JPEG) and enforce a reasonable size limit.
- Generate safe storage names instead of trusting user-supplied filenames.
- Do not execute uploaded files or serve them as executable content.
- Make source-document access private and available only to the authorized patient and hospital staff reviewing it.
- Do not expose local file paths or storage credentials in API responses.
- If reliable OCR is unavailable, say that extraction was not available. Do not fabricate extracted values.
- Mark fields that are uncertain or unreadable and let a reviewer inspect the original source.
- Preserve the original uploaded document and keep extracted fields as a separate draft until reviewed.

For a quick demo, local file storage may work temporarily, but files stored on an ephemeral deployment filesystem may disappear on redeploy/restart. If the upload feature is part of the live demo, choose storage that persists or explicitly disclose the demo limitation. Do not put uploaded documents inside a public static directory.

## 13. Security, Privacy, and Clinical Boundaries

- Use synthetic patients and fabricated medical history only for demonstrations.
- No real patient data should be used in the hackathon, screenshots, test fixtures, logs, or public repository.
- Enforce authorization on the backend, not just by hiding buttons in React.
- A patient must only access records associated with their authenticated identity.
- Validate and constrain all user input; use parameterized database queries/ORM operations.
- Store password hashes, not passwords, if password-based login is implemented.
- Keep secrets in the hosting provider's environment configuration.
- Avoid logging sensitive document contents or full patient details.
- Include a clear demo disclaimer: “Prototype for demonstration only. Not for real clinical use.”
- Do not claim regulatory compliance, record authenticity, clinical accuracy, or production readiness without independent validation.

## 14. Acceptance Criteria / Definition of Done

The prototype is ready to present when all of the following pass:

- [ ] The public landing page loads from its live URL.
- [ ] The backend health endpoint responds successfully.
- [ ] Staff can register a synthetic patient and receive a unique Patient ID.
- [ ] The new patient appears in the patient list after refresh.
- [ ] Staff can add a visit/note and retrieve it later.
- [ ] The patient can sign in using the intended demo flow.
- [ ] The patient sees only their own saved records.
- [ ] A patient record summary can be printed or saved as PDF through the browser.
- [ ] A patient can upload an allowed external document, or receive a clear and honest error if upload is not configured.
- [ ] An imported document is marked as pending review by default.
- [ ] Staff can approve or reject the pending submission.
- [ ] Rejected or pending external information does not appear as an approved official record.
- [ ] The frontend uses the deployed backend base URL in production.
- [ ] CORS and environment variables are configured correctly.
- [ ] No real patient information or secrets are present in the repository.
- [ ] The team has tested the complete flow from the live URL, not just on localhost.

## 15. Build Plan for a Three-Hour Session

Use short, testable increments. Do not ask the coding assistant to generate the entire system in one uncontrolled pass.

### Phase 1 — Inspect and plan (0–15 minutes)
- Inspect the existing repository, runtime, installed dependencies, and current environment variables.
- Confirm whether React/FastAPI projects already exist. Do not overwrite working code.
- Identify the smallest end-to-end slice and list the exact files to create or change.

### Phase 2 — Core backend (15–60 minutes)
- Configure FastAPI and database connection.
- Implement patient model and registration/list/detail routes.
- Implement visit creation and history retrieval.
- Add input validation and clear errors.
- Test with Swagger `/docs` before integrating React.

### Phase 3 — Frontend integration (60–105 minutes)
- Connect staff patient registration/list/detail screens to the real API.
- Connect add-visit flow and confirm the newly created visit appears after refresh.
- Keep API URLs in an environment variable.

### Phase 4 — Patient portal and portability (105–145 minutes)
- Add the simplified demo patient sign-in and read-only record view.
- Add print-friendly record summary.
- Add external-document upload and pending-review status if core flows are stable.

### Phase 5 — Deploy and verify (145–180 minutes)
- Deploy the backend to Render and confirm the health endpoint and `/docs` work.
- Confirm Neon database connectivity and persistence.
- Set the frontend production API URL and deploy to Vercel.
- Configure CORS.
- Test patient registration → add visit → patient view → print from the live frontend.
- Test an external upload/review if implemented.
- Prepare a small set of synthetic demo accounts and data.

**Rule:** If deployment is at risk, stop adding features and get the core patient registration/history workflow live first. A small working product is preferable to a large untested codebase.

## 16. How Claude Code Should Work on This Project

When this document is provided, follow these instructions:

1. Start by inspecting the repository and explaining the existing structure in a few lines.
2. Identify the current state of the frontend, backend, database, tests, and deployment configuration.
3. Do not assume that a file, endpoint, dependency, or environment variable exists; verify it.
4. Give a concise implementation plan ordered by the MVP priorities above.
5. Build one vertical slice at a time. After each slice, run the relevant checks or provide exact commands for the developer to run.
6. Do not replace the existing framework or rewrite working files without a clear reason.
7. Do not invent API endpoints or allow the frontend to call PostgreSQL directly.
8. Keep a single, documented API contract so the separate frontend developer can integrate independently.
9. Add `.env.example` containing variable names and placeholders only; never put real secrets into source code.
10. If required configuration is missing, explain exactly what value or action is needed rather than silently guessing.
11. Keep the implementation appropriate for a three-hour hackathon. Prioritize working flows, useful error handling, accessibility, and live deployment over overengineering.
12. Use only synthetic demo data. Keep external imports pending review and preserve the source document.
13. Be explicit about tests that passed, tests that failed, and anything still mocked or incomplete. Never claim deployment succeeded unless it was actually verified.

### First instruction to Claude Code

> Read `MedVerify_Product_Brief_for_Claude.md` completely. First inspect the repository and summarize what is already present. Then propose the smallest implementation plan that can produce a working live demo within three hours. Do not start by generating the entire application. Identify the first vertical slice, the files you will touch, required environment variables, and the exact commands to run and test it. Wait for my confirmation before making large structural changes. Keep the frontend/API contract clear because another developer is building the React UI on a separate laptop.

---

## 17. Suggested Demo Story

1. A staff member registers “Ada Example” and receives a unique MedVerify Patient ID.
2. Staff adds a visit and a lab-result entry using clearly synthetic information.
3. Ada signs into the patient portal and views her record history.
4. Ada downloads or prints the record to take to a hospital that does not use MedVerify.
5. Ada uploads a sample image/PDF of an old record. MedVerify preserves the source and shows extracted draft fields, or clearly explains that automated extraction is unavailable.
6. The item appears as pending review on the staff dashboard.
7. Staff reviews the source and extracted fields, then approves or rejects the submission.
8. The UI clearly distinguishes the official record from external documents that have not been approved.

**Core message:** MedVerify gives patients a practical way to carry their medical history while keeping official records under authorized hospital control and preserving the source of imported information.
