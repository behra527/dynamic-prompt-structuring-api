
import json

from openai import OpenAI

from app.config import settings
from app.prompt_builder import build_system_prompt
from app.schemas import PromptRequest
from app.validator import validate_clinical_response


def generate_note(request: PromptRequest) -> dict:
    context = request.patient_context

    # Collect only information supplied in the request.
    observations = list(context.symptoms)
    observations.extend(context.relevant_history)

    if context.medications:
        observations.append(
            f"Reported medications: {', '.join(context.medications)}"
        )

    if context.allergies:
        observations.append(
            f"Reported allergies: {', '.join(context.allergies)}"
        )

    # Track information that was not provided.
    missing = []

    if context.age is None:
        missing.append("Patient age")

    if not context.symptoms:
        missing.append("Symptoms")

    if not context.vitals:
        missing.append("Vital signs")

    if not context.relevant_history:
        missing.append("Relevant medical history")

    if not context.medications:
        missing.append("Medication information")

    if not context.allergies:
        missing.append("Allergy information")

    # Demo mode when no API key is configured.
    if not settings.api_key:
        demo_response = {
            "note_type": request.note_type.value,
            "output_format": request.output_format.value,
            "summary": (
                f"Demo response for {request.note_type.value}. "
                "Only supplied information is available. "
                "This is not a clinical assessment."
            ),
            "key_observations": observations[:30],
            "missing_information": missing[:30],
            "disclaimer": (
                "Demo mode: no language model was called. "
                "Qualified human review is required before clinical use."
            ),
        }

        validated = validate_clinical_response(demo_response)
        return validated.model_dump(mode="json")

    # Configure the API client.
    client_options = {"api_key": settings.api_key}

    if settings.base_url:
        client_options["base_url"] = settings.base_url

    client = OpenAI(**client_options)

    # Request a JSON response from the configured model.
    response = client.chat.completions.create(
        model=settings.model,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": build_system_prompt(request),
            },
            {
                "role": "user",
                "content": json.dumps(
                    request.model_dump(mode="json"),
                    ensure_ascii=False,
                ),
            },
        ],
    )

    # Inspect the response before parsing it.
    if not response.choices:
        raise ValueError(
            "The API returned no choices. "
            f"Model: {settings.model}. "
            f"Response ID: {response.id}"
        )

    choice = response.choices[0]
    message = choice.message
    content = message.content

    if not content or not content.strip():
        finish_reason = choice.finish_reason
        refusal = getattr(message, "refusal", None)

        raise ValueError(
            "The model returned no text content. "
            f"Finish reason: {finish_reason}. "
            f"Refusal: {refusal!r}. "
            "Check the provider response and model support."
        )

    # Validate the model's JSON against the Pydantic schema.
    validated = validate_clinical_response(content)
    result = validated.model_dump(mode="json")

    # Ensure missing medication and allergy information is listed.
    result["missing_information"] = list(
        dict.fromkeys(
            result["missing_information"] + missing
        )
    )[:30]

    # Add observations derived from supplied information.
    result["key_observations"] = list(
        dict.fromkeys(
            result["key_observations"] + observations
        )
    )[:30]

    # Validate the final response after updating its fields.
    final_response = validate_clinical_response(result)

    return final_response.model_dump(mode="json")