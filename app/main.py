
import logging

from fastapi import FastAPI, HTTPException, Security
from openai import APIConnectionError, APIStatusError, OpenAIError
from pydantic import ValidationError

from app.auth import require_api_key
from app.llm_client import generate_note
from app.middleware import RequestSizeLimitMiddleware
from app.schemas import ClinicalNoteResponse, PromptRequest
from app.validator import validate_clinical_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dynamic Prompt Structuring API",
    version="1.0.0",
    description="Role-based structured clinical documentation demo.",
)

app.add_middleware(
    RequestSizeLimitMiddleware,
    max_body_size=64 * 1024,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/generate-note",
    response_model=ClinicalNoteResponse,
    dependencies=[Security(require_api_key)],
)
def create_note(request: PromptRequest):
    try:
        raw_response = generate_note(request)
        return validate_clinical_response(raw_response)

    except (ValidationError, ValueError) as exc:
        logger.error(
            "Response validation failed (%s)",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=502,
            detail="Model response was invalid. Check server logs.",
        ) from exc

    except APIStatusError as exc:
        logger.error(
            "LLM provider returned HTTP %s (%s)",
            exc.status_code,
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=502,
            detail=(
                f"LLM provider request failed (HTTP {exc.status_code}). "
                "Check server logs and API configuration."
            ),
        ) from exc

    except APIConnectionError as exc:
        logger.error(
            "Could not connect to the LLM provider (%s)",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=502,
            detail=(
                "Could not connect to the LLM provider. "
                "Check network and server logs."
            ),
        ) from exc

    except OpenAIError as exc:
        logger.error(
            "LLM client error (%s)",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=502,
            detail=(
                f"LLM client error: {type(exc).__name__}. "
                "Check server logs."
            ),
        ) from exc

    except Exception as exc:
        logger.error(
            "Unexpected note generation error (%s)",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error. Check server logs.",
        ) from exc