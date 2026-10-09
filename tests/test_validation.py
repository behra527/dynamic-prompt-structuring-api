
import json

import pytest
from pydantic import ValidationError

from app.validator import validate_clinical_response


def valid_response():
    return {
        "note_type": "clinical_summary",
        "output_format": "standard_json",
        "summary": "Patient reports headache.",
        "key_observations": ["Headache reported"],
        "missing_information": ["Vital signs"],
        "disclaimer": "Qualified human review is required.",
    }


def test_valid_response_is_accepted():
    result = validate_clinical_response(valid_response())

    assert result.note_type == "clinical_summary"
    assert result.summary == "Patient reports headache."


def test_valid_json_string_is_accepted():
    raw_json = json.dumps(valid_response())

    result = validate_clinical_response(raw_json)

    assert result.output_format == "standard_json"


def test_missing_required_field_is_rejected():
    data = valid_response()
    del data["summary"]

    with pytest.raises(ValidationError):
        validate_clinical_response(data)


def test_invalid_note_type_is_rejected():
    data = valid_response()
    data["note_type"] = "unknown_note"

    with pytest.raises(ValidationError):
        validate_clinical_response(data)


def test_unexpected_field_is_rejected():
    data = valid_response()
    data["extra_field"] = "unexpected"

    with pytest.raises(ValidationError):
        validate_clinical_response(data)


def test_malformed_json_is_rejected():
    with pytest.raises(json.JSONDecodeError):
        validate_clinical_response('{"summary": ')


def test_json_with_surrounding_whitespace_is_accepted():
    raw_json = f"  \n{json.dumps(valid_response())}\n  "

    result = validate_clinical_response(raw_json)

    assert result.summary == "Patient reports headache."


def test_json_markdown_fence_is_accepted():
    raw_json = (
        "```json\n"
        + json.dumps(valid_response())
        + "\n```"
    )

    result = validate_clinical_response(raw_json)

    assert result.note_type == "clinical_summary"


def test_plain_markdown_fence_is_accepted():
    raw_json = (
        "```\n"
        + json.dumps(valid_response())
        + "\n```"
    )

    result = validate_clinical_response(raw_json)

    assert result.output_format == "standard_json"


def test_empty_response_is_rejected():
    with pytest.raises(ValueError, match="empty"):
        validate_clinical_response("   ")


def test_incomplete_markdown_fence_is_rejected():
    with pytest.raises(ValueError, match="Markdown code fence"):
        validate_clinical_response(
            '```json\n{"summary": "incomplete"}'
        )


@pytest.mark.parametrize(
    "raw_response",
    [
        "[]",
        '"just text"',
        "123",
        "null",
    ],
)
def test_non_object_json_is_rejected(raw_response):
    with pytest.raises(ValueError, match="JSON object"):
        validate_clinical_response(raw_response)


def test_unsupported_input_type_is_rejected():
    with pytest.raises(TypeError, match="JSON string or dictionary"):
        validate_clinical_response(123)