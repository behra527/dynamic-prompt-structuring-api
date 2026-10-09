
import json
from types import SimpleNamespace

import pytest
from openai import APIStatusError
from pydantic import ValidationError

import app.llm_client as llm_client
from app.schemas import PromptRequest


def make_request():
    return PromptRequest(
        user_role="medical_scribe",
        patient_context={
            "age": 45,
            "symptoms": ["Headache"],
            "relevant_history": ["Hypertension"],
            "medications": [],
            "allergies": [],
            "vitals": {},
        },
        note_type="clinical_summary",
        output_format="standard_json",
        user_instruction="Summarize the supplied information.",
    )


def valid_model_response():
    return {
        "note_type": "clinical_summary",
        "output_format": "standard_json",
        "summary": "The patient reports a headache.",
        "key_observations": ["Headache reported"],
        "missing_information": [],
        "disclaimer": "Qualified human review is required.",
    }


def fake_completion(content, finish_reason="stop", refusal=None):
    message = SimpleNamespace(
        content=content,
        refusal=refusal,
    )
    choice = SimpleNamespace(
        message=message,
        finish_reason=finish_reason,
    )
    return SimpleNamespace(
        choices=[choice],
        id="test-response-id",
    )


def mock_client(monkeypatch, completion):
    class FakeCompletions:
        def create(self, **kwargs):
            return completion

    class FakeChat:
        completions = FakeCompletions()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = FakeChat()

    monkeypatch.setattr(llm_client, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(llm_client.settings, "api_key", "test-key")
    monkeypatch.setattr(
        llm_client.settings,
        "base_url",
        "https://example.test/v1",
    )
    monkeypatch.setattr(
        llm_client.settings,
        "model",
        "test-model",
    )


def test_demo_mode_returns_valid_response(monkeypatch):
    monkeypatch.setattr(llm_client.settings, "api_key", "")

    result = llm_client.generate_note(make_request())

    assert result["note_type"] == "clinical_summary"
    assert "Medication information" in result["missing_information"]
    assert "Allergy information" in result["missing_information"]


def test_valid_model_response_is_accepted(monkeypatch):
    payload = valid_model_response()
    mock_client(
        monkeypatch,
        fake_completion(json.dumps(payload)),
    )

    result = llm_client.generate_note(make_request())

    assert result["summary"] == payload["summary"]
    assert "Medication information" in result["missing_information"]
    assert "Allergy information" in result["missing_information"]


def test_empty_model_response_raises_value_error(monkeypatch):
    mock_client(monkeypatch, fake_completion(""))

    with pytest.raises(ValueError, match="no text content"):
        llm_client.generate_note(make_request())


def test_invalid_json_is_rejected(monkeypatch):
    mock_client(monkeypatch, fake_completion("{invalid json"))

    with pytest.raises(json.JSONDecodeError):
        llm_client.generate_note(make_request())


def test_invalid_schema_is_rejected(monkeypatch):
    payload = valid_model_response()
    payload["note_type"] = "unknown_note"

    mock_client(
        monkeypatch,
        fake_completion(json.dumps(payload)),
    )

    with pytest.raises(ValidationError):
        llm_client.generate_note(make_request())


def test_provider_api_error_propagates(monkeypatch):
    error_response = SimpleNamespace(
        status_code=503,
        headers={},
        request=None,
    )
    provider_error = APIStatusError(
        "Provider unavailable",
        response=error_response,
        body=None,
    )

    class FakeCompletions:
        def create(self, **kwargs):
            raise provider_error

    class FakeChat:
        completions = FakeCompletions()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = FakeChat()

    monkeypatch.setattr(llm_client, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(llm_client.settings, "api_key", "test-key")
    monkeypatch.setattr(
        llm_client.settings,
        "base_url",
        "https://example.test/v1",
    )
    monkeypatch.setattr(
        llm_client.settings,
        "model",
        "test-model",
    )

    with pytest.raises(APIStatusError):
        llm_client.generate_note(make_request())