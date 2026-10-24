"""External records: patient upload, file access, staff review, and the rule that
nothing becomes official until a staff member approves it."""

import uuid

import pytest

from app.routers import external_records as ext

from .conftest import HTML_BYTES, JPEG_BYTES, PDF_BYTES, PNG_BYTES

UPLOAD_URL = "/api/v1/patients/me/external-records"
STAFF_URL = "/api/v1/staff/external-records"

RECORD_KEYS = {
    "id", "patient_id", "patient_code", "patient_name", "original_filename", "content_type",
    "size_bytes", "source_facility", "document_date", "document_type", "notes",
    "extraction_status", "review_status", "review_note", "reviewed_by", "reviewed_at", "uploaded_at",
}


@pytest.fixture
def upload(client, patient_headers):
    """Upload as the default test patient; returns the response."""

    def _upload(content=PNG_BYTES, filename="lab.png", content_type="image/png", headers=None, **fields):
        return client.post(
            UPLOAD_URL,
            files={"file": (filename, content, content_type)},
            data=fields,
            headers=patient_headers if headers is None else headers,
        )

    return _upload


@pytest.fixture
def uploaded(upload):
    r = upload(
        source_facility="Sample General Hospital",
        document_date="2024-03-02",
        document_type="lab_result",
        notes="Synthetic: haemoglobin 13.1 g/dL",
    )
    assert r.status_code == 201, r.text
    return r.json()


def _official_records(client, headers):
    return client.get("/api/v1/patients/me/records", headers=headers).json()


# --- upload ---


def test_upload_creates_pending_record(uploaded, patient):
    assert set(uploaded) == RECORD_KEYS
    assert uploaded["patient_id"] == patient["id"]
    assert uploaded["patient_code"] == patient["patient_code"]
    assert uploaded["patient_name"] == patient["full_name"]
    assert uploaded["original_filename"] == "lab.png"
    assert uploaded["content_type"] == "image/png"
    assert uploaded["size_bytes"] == len(PNG_BYTES)
    assert uploaded["source_facility"] == "Sample General Hospital"
    assert uploaded["document_date"] == "2024-03-02"
    assert uploaded["document_type"] == "lab_result"
    assert uploaded["notes"] == "Synthetic: haemoglobin 13.1 g/dL"
    assert uploaded["extraction_status"] == "not_available"  # no OCR, stated honestly
    assert uploaded["review_status"] == "pending_review"
    assert uploaded["review_note"] is None and uploaded["reviewed_by"] is None and uploaded["reviewed_at"] is None
    assert uploaded["uploaded_at"].endswith("Z")
    assert "file_data" not in uploaded


@pytest.mark.parametrize(
    "content, sent_type, expected",
    [
        (PDF_BYTES, "application/octet-stream", "application/pdf"),
        (JPEG_BYTES, "image/png", "image/jpeg"),  # client label is ignored
        (PNG_BYTES, "application/pdf", "image/png"),
    ],
)
def test_upload_type_detected_from_content(upload, content, sent_type, expected):
    r = upload(content=content, filename="doc.bin", content_type=sent_type)
    assert r.status_code == 201 and r.json()["content_type"] == expected


def test_upload_optional_fields_blank_become_null(upload):
    r = upload(source_facility="  ", document_date="", document_type="", notes="  ")
    assert r.status_code == 201
    body = r.json()
    assert body["source_facility"] is None and body["document_date"] is None
    assert body["document_type"] is None and body["notes"] is None


def test_upload_filename_is_sanitised(upload):
    r = upload(filename="../../evil<script>.png")
    assert r.status_code == 201 and r.json()["original_filename"] == "evil_script_.png"


def test_upload_rejects_disguised_file(upload):
    r = upload(content=HTML_BYTES, filename="photo.png", content_type="image/png")
    assert r.status_code == 415
    assert r.json() == {"detail": "Only PDF, PNG or JPEG files are allowed"}


def test_upload_rejects_too_large(upload):
    big = b"%PDF-1.4\n" + b"0" * ext.MAX_UPLOAD_BYTES
    r = upload(content=big, filename="big.pdf", content_type="application/pdf")
    assert r.status_code == 413


def test_upload_accepts_exactly_max_size(upload):
    exact = b"%PDF-1.4\n" + b"0" * (ext.MAX_UPLOAD_BYTES - 9)
    assert len(exact) == ext.MAX_UPLOAD_BYTES
    r = upload(content=exact, filename="max.pdf", content_type="application/pdf")
    assert r.status_code == 201 and r.json()["size_bytes"] == ext.MAX_UPLOAD_BYTES


def test_upload_rejects_empty_file(upload):
    r = upload(content=b"")
    assert r.status_code == 422 and r.json() == {"detail": "File is empty"}


def test_upload_requires_file(client, patient_headers):
    assert client.post(UPLOAD_URL, data={"notes": "x"}, headers=patient_headers).status_code == 422


@pytest.mark.parametrize(
    "fields",
    [
        {"document_date": "03/02/2024"},
        {"document_date": "2999-01-01"},
        {"source_facility": "x" * 201},
        {"document_type": "x" * 51},
        {"notes": "x" * 5001},
    ],
)
def test_upload_field_validation(upload, fields):
    assert upload(**fields).status_code == 422


def test_upload_requires_patient(client, upload, staff_headers):
    assert client.post(UPLOAD_URL, files={"file": ("a.png", PNG_BYTES, "image/png")}).status_code == 401
    assert upload(headers=staff_headers).status_code == 403


# --- patient list & file access ---


def test_patient_lists_own_uploads(client, upload, patient_headers):
    a = upload().json()
    b = upload(content=PDF_BYTES, filename="b.pdf").json()
    r = client.get(UPLOAD_URL, headers=patient_headers)
    assert r.status_code == 200
    assert {x["id"] for x in r.json()} == {a["id"], b["id"]}


def test_patient_cannot_see_others_uploads(client, uploaded, make_patient, login_patient):
    other = login_patient(make_patient())
    assert client.get(UPLOAD_URL, headers=other).json() == []
    assert client.get(f"{UPLOAD_URL}/{uploaded['id']}/file", headers=other).status_code == 404


def test_patient_downloads_own_file(client, uploaded, patient_headers):
    r = client.get(f"{UPLOAD_URL}/{uploaded['id']}/file", headers=patient_headers)
    assert r.status_code == 200
    assert r.content == PNG_BYTES
    assert r.headers["content-type"] == "image/png"
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["cache-control"] == "private, no-store"
    assert r.headers["content-disposition"] == 'inline; filename="lab.png"'


def test_patient_file_unknown_or_malformed_id(client, patient_headers):
    assert client.get(f"{UPLOAD_URL}/{uuid.uuid4()}/file", headers=patient_headers).status_code == 404
    assert client.get(f"{UPLOAD_URL}/nope/file", headers=patient_headers).status_code == 422


def test_patient_list_and_file_require_patient(client, uploaded, staff_headers):
    for url in (UPLOAD_URL, f"{UPLOAD_URL}/{uploaded['id']}/file"):
        assert client.get(url).status_code == 401
        assert client.get(url, headers=staff_headers).status_code == 403


# --- staff list / detail / file ---


def test_staff_lists_pending(client, staff_headers, uploaded):
    r = client.get(STAFF_URL, params={"status": "pending_review"}, headers=staff_headers)
    assert r.status_code == 200
    assert uploaded["id"] in {x["id"] for x in r.json()}
    assert all(x["review_status"] == "pending_review" for x in r.json())


def test_staff_list_without_filter_includes_all_statuses(client, staff_headers, upload):
    pending = upload().json()
    rejected = upload().json()
    client.post(f"{STAFF_URL}/{rejected['id']}/reject", json={}, headers=staff_headers)
    ids = {x["id"] for x in client.get(STAFF_URL, headers=staff_headers).json()}
    assert {pending["id"], rejected["id"]} <= ids


def test_staff_status_filter(client, staff_headers, upload):
    approved = upload().json()
    client.post(f"{STAFF_URL}/{approved['id']}/approve", json={}, headers=staff_headers)
    approved_ids = {x["id"] for x in client.get(STAFF_URL, params={"status": "approved"}, headers=staff_headers).json()}
    pending_ids = {x["id"] for x in client.get(STAFF_URL, params={"status": "pending_review"}, headers=staff_headers).json()}
    assert approved["id"] in approved_ids and approved["id"] not in pending_ids


def test_staff_invalid_status_filter(client, staff_headers):
    assert client.get(STAFF_URL, params={"status": "bogus"}, headers=staff_headers).status_code == 422


def test_staff_detail_and_file(client, staff_headers, uploaded):
    r = client.get(f"{STAFF_URL}/{uploaded['id']}", headers=staff_headers)
    assert r.status_code == 200 and r.json() == uploaded
    f = client.get(f"{STAFF_URL}/{uploaded['id']}/file", headers=staff_headers)
    assert f.status_code == 200 and f.content == PNG_BYTES and f.headers["content-type"] == "image/png"


def test_staff_unknown_record(client, staff_headers):
    rid = uuid.uuid4()
    assert client.get(f"{STAFF_URL}/{rid}", headers=staff_headers).status_code == 404
    assert client.get(f"{STAFF_URL}/{rid}/file", headers=staff_headers).status_code == 404


def test_staff_routes_require_staff(client, uploaded, patient_headers):
    rid = uploaded["id"]
    for method, url in (
        ("get", STAFF_URL),
        ("get", f"{STAFF_URL}/{rid}"),
        ("get", f"{STAFF_URL}/{rid}/file"),
        ("post", f"{STAFF_URL}/{rid}/approve"),
        ("post", f"{STAFF_URL}/{rid}/reject"),
    ):
        kwargs = {"json": {}} if method == "post" else {}
        assert getattr(client, method)(url, **kwargs).status_code == 401, url
        assert getattr(client, method)(url, headers=patient_headers, **kwargs).status_code == 403, url


# --- review: approve / reject ---


def test_pending_upload_is_not_in_official_record(client, uploaded, patient_headers):
    assert _official_records(client, patient_headers) == []


def test_approve_creates_linked_official_entry(client, staff_headers, uploaded, patient, patient_headers):
    r = client.post(f"{STAFF_URL}/{uploaded['id']}/approve", json={"review_note": "Checked."}, headers=staff_headers)
    assert r.status_code == 200
    reviewed = r.json()
    assert reviewed["review_status"] == "approved"
    assert reviewed["review_note"] == "Checked."
    assert reviewed["reviewed_by"] == "Demo Staff"
    assert reviewed["reviewed_at"].endswith("Z")

    records = _official_records(client, patient_headers)
    assert len(records) == 1
    entry = records[0]
    assert entry["record_type"] == "external_import"
    assert entry["source_external_record_id"] == uploaded["id"]
    assert entry["patient_id"] == patient["id"]
    assert entry["visit_date"] == "2024-03-02"  # taken from document_date
    assert entry["title"] == "External lab_result from Sample General Hospital"
    assert entry["details"] == "Synthetic: haemoglobin 13.1 g/dL"
    assert entry["created_by"] == "Demo Staff"


def test_approve_without_details_uses_fallbacks(client, staff_headers, upload, patient_headers):
    bare = upload().json()
    client.post(f"{STAFF_URL}/{bare['id']}/approve", json={}, headers=staff_headers)
    entry = _official_records(client, patient_headers)[0]
    assert entry["title"] == "External document from unknown facility"
    assert entry["visit_date"] == bare["uploaded_at"][:10]  # upload date when document_date unknown
    assert entry["details"] is None


def test_patient_sees_review_outcome(client, staff_headers, uploaded, patient_headers):
    client.post(f"{STAFF_URL}/{uploaded['id']}/reject", json={"review_note": "Unreadable."}, headers=staff_headers)
    mine = client.get(UPLOAD_URL, headers=patient_headers).json()
    assert [(x["review_status"], x["review_note"]) for x in mine] == [("rejected", "Unreadable.")]


def test_reject_adds_nothing_to_official_record(client, staff_headers, uploaded, patient_headers):
    r = client.post(f"{STAFF_URL}/{uploaded['id']}/reject", json={"review_note": "  "}, headers=staff_headers)
    assert r.status_code == 200
    assert r.json()["review_status"] == "rejected"
    assert r.json()["review_note"] is None  # blank note stored as null
    assert r.json()["reviewed_by"] == "Demo Staff"
    assert _official_records(client, patient_headers) == []


@pytest.mark.parametrize("first, second", [("approve", "approve"), ("approve", "reject"), ("reject", "approve"), ("reject", "reject")])
def test_cannot_review_twice(client, staff_headers, uploaded, patient_headers, first, second):
    assert client.post(f"{STAFF_URL}/{uploaded['id']}/{first}", json={}, headers=staff_headers).status_code == 200
    r = client.post(f"{STAFF_URL}/{uploaded['id']}/{second}", json={}, headers=staff_headers)
    assert r.status_code == 409 and r.json()["detail"].startswith("Already reviewed")
    # Still at most one official entry.
    assert len(_official_records(client, patient_headers)) == (1 if first == "approve" else 0)


def test_review_unknown_record(client, staff_headers):
    for action in ("approve", "reject"):
        assert client.post(f"{STAFF_URL}/{uuid.uuid4()}/{action}", json={}, headers=staff_headers).status_code == 404


def test_review_note_too_long(client, staff_headers, uploaded):
    r = client.post(f"{STAFF_URL}/{uploaded['id']}/approve", json={"review_note": "x" * 1001}, headers=staff_headers)
    assert r.status_code == 422


def test_review_only_affects_that_patient(client, staff_headers, uploaded, make_patient, login_patient):
    other = login_patient(make_patient())
    client.post(f"{STAFF_URL}/{uploaded['id']}/approve", json={}, headers=staff_headers)
    assert _official_records(client, other) == []
