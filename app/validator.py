
import json
import re
from typing import Any

from pydantic import ValidationError

from app.schemas import ClinicalNoteResponse


def _parse_json_response(raw_response: str | dict) -> dict[str, Any]:
    if isinstance(raw_response, dict):
        return raw_response

    if not isinstance(raw_response, str):
        raise TypeError(
            "Model response must be a JSON string or dictionary."
        )

    cleaned = raw_response.strip()

    if not cleaned:
        raise ValueError("Model response is empty.")

    # Remove a complete Markdown code fence, if present.
    if cleaned.startswith("```"):
        match = re.fullmatch(
            r"```(?:json)?\s*\n(.*?)\n```",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if not match:
            raise ValueError(
                "Model response contains an invalid Markdown code fence."
            )

        cleaned = match.group(1).strip()

    parsed = json.loads(cleaned)

    if not isinstance(parsed, dict):
        raise ValueError(
            "Model response must contain a JSON object."
        )

    return parsed


def validate_clinical_response(
    raw_response: str | dict,
) -> ClinicalNoteResponse:
    data = _parse_json_response(raw_response)
    return ClinicalNoteResponse.model_validate(data)