
import pytest
from pydantic import ValidationError

from app.schemas import (
    ClinicalNoteResponse,
    NoteType,
    OutputFormat,
    PromptRequest,
    UserRole,
)


def valid_request():
    return {
        "user_role": "doctor",
        "patient_context": {
            "age": 45,
            "symptoms": ["fatigue", "headache"],
        },
        "note_type": "clinical_summary",
        "output_format": "standard_json",
        "user_instruction": "Summarize the supplied information.",
    }


def test_valid_prompt_request():
    request = PromptRequest.model_validate(valid_request())

    assert request.user_role == UserRole.DOCTOR
    assert request.patient_context.age == 45
    assert request.note_type == NoteType.CLINICAL_SUMMARY


def test_patient_context_defaults():
    data = valid_request()
    data.pop("patient_context")

    request = PromptRequest.model_validate(data)

    assert request.patient_context.age is None
    assert request.patient_context.symptoms == []


def test_invalid_patient_age_is_rejected():
    data = valid_request()
    data["patient_context"]["age"] = 150

    with pytest.raises(ValidationError):
        PromptRequest.model_validate(data)


def test_unsupported_role_is_rejected():
    data = valid_request()
    data["user_role"] = "administrator"

    with pytest.raises(ValidationError):
        PromptRequest.model_validate(data)


def test_unexpected_request_field_is_rejected():
    data = valid_request()
    data["unexpected_field"] = "not allowed"

    with pytest.raises(ValidationError):
        PromptRequest.model_validate(data)


def test_missing_response_field_is_rejected():
    data = {
        "note_type": "clinical_summary",
        "output_format": "standard_json",
        "summary": "Patient-reported fatigue.",
        "key_observations": ["Fatigue"],
        "missing_information": ["Symptom duration"],
    }

    with pytest.raises(ValidationError):
        ClinicalNoteResponse.model_validate(data)


def test_valid_structured_response():
    response = ClinicalNoteResponse.model_validate({
        "note_type": "clinical_summary",
        "output_format": "standard_json",
        "summary": "Patient-reported fatigue.",
        "key_observations": ["Fatigue"],
        "missing_information": ["Symptom duration"],
        "disclaimer": "Review for accuracy before clinical use.",
    })

    assert response.summary == "Patient-reported fatigue."
    assert response.output_format == OutputFormat.STANDARD_JSON


def test_symptom_entry_over_300_characters_is_rejected():
    data = valid_request()
    data["patient_context"]["symptoms"] = ["x" * 301]

    with pytest.raises(ValidationError):
        PromptRequest.model_validate(data)


def test_more_than_30_vitals_are_rejected():
    data = valid_request()
    data["patient_context"]["vitals"] = {
        f"vital_{index}": index
        for index in range(31)
    }

    with pytest.raises(ValidationError):
        PromptRequest.model_validate(data)


def test_vital_key_over_50_characters_is_rejected():
    data = valid_request()
    data["patient_context"]["vitals"] = {
        "x" * 51: "normal"
    }

    with pytest.raises(ValidationError):
        PromptRequest.model_validate(data)


def test_empty_symptom_entry_is_rejected():
    data = valid_request()
    data["patient_context"]["symptoms"] = [""]

    with pytest.raises(ValidationError):
        PromptRequest.model_validate(data)