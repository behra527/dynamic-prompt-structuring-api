
import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.config import settings


client = TestClient(main.app)

TEST_API_KEY = "test-api-key-for-unit-tests"
MAX_REQUEST_BODY_SIZE = 64 * 1024
AUTH_HEADERS = {"X-API-Key": TEST_API_KEY}


@pytest.fixture(autouse=True)
def configure_test_api_key(monkeypatch):
    monkeypatch.setattr(
        settings,
        "app_api_key",
        TEST_API_KEY,
    )


def valid_request():
    return {
        "user_role": "medical_scribe",
        "patient_context": {
            "age": 45,
            "symptoms": ["Headache"],
            "relevant_history": ["Hypertension"],
            "medications": [],
            "allergies": [],
            "vitals": {},
        },
        "note_type": "clinical_summary",
        "output_format": "standard_json",
        "user_instruction": "Summarize the supplied information.",
    }


def valid_response():
    return {
        "note_type": "clinical_summary",
        "output_format": "standard_json",
        "summary": "The patient reports a headache.",
        "key_observations": [
            "Headache",
            "Hypertension history",
        ],
        "missing_information": [
            "Vital signs",
            "Medication information",
            "Allergy information",
        ],
        "disclaimer": "Qualified human review is required.",
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_note_requires_api_key():
    response = client.post(
        "/generate-note",
        json=valid_request(),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid or missing API key."
    )


def test_generate_note_rejects_invalid_api_key():
    response = client.post(
        "/generate-note",
        json=valid_request(),
        headers={"X-API-Key": "wrong-api-key"},
    )

    assert response.status_code == 401


def test_generate_note_success(monkeypatch):
    monkeypatch.setattr(
        main,
        "generate_note",
        lambda request: valid_response(),
    )

    response = client.post(
        "/generate-note",
        json=valid_request(),
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["note_type"] == "clinical_summary"
    assert response.json()["summary"] == (
        "The patient reports a headache."
    )


def test_invalid_request_returns_422():
    request_data = valid_request()
    request_data["user_role"] = "unknown_role"

    response = client.post(
        "/generate-note",
        json=request_data,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 422


def test_missing_instruction_returns_422():
    request_data = valid_request()
    del request_data["user_instruction"]

    response = client.post(
        "/generate-note",
        json=request_data,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 422


def test_invalid_model_response_returns_502(monkeypatch):
    monkeypatch.setattr(
        main,
        "generate_note",
        lambda request: {
            "note_type": "invalid_note_type",
        },
    )

    response = client.post(
        "/generate-note",
        json=valid_request(),
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Model response was invalid. Check server logs."
    )


def test_unexpected_error_returns_500(monkeypatch):
    def raise_unexpected_error(request):
        raise RuntimeError("Test-only unexpected error")

    monkeypatch.setattr(
        main,
        "generate_note",
        raise_unexpected_error,
    )

    response = client.post(
        "/generate-note",
        json=valid_request(),
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Unexpected server error. Check server logs."
    )


def test_oversized_request_returns_413():
    oversized_body = b"x" * (MAX_REQUEST_BODY_SIZE + 1)

    response = client.post(
        "/generate-note",
        content=oversized_body,
        headers={
            "content-type": "application/json",
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == (
        "Request body exceeds the 64 KB limit."
    )