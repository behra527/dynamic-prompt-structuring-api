
# Dynamic Prompt Structuring API

A FastAPI application that creates structured clinical documentation using role-based prompts, input validation, and an LLM integration.

## Features

- Role-based dynamic prompt construction
- Pydantic request and response validation
- LLM integration through an OpenAI-compatible API
- API-key authentication for note generation
- Request-size limit of 64 KB
- Error handling for invalid model responses and provider failures
- Demo mode when no provider API key is configured
- Automated tests with pytest

## Tech Stack

- Python 3.13
- FastAPI
- Pydantic and Pydantic Settings
- OpenAI Python SDK
- Pytest

## Setup

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project root using `.env.example` as a reference.

Configure the following variables:

- `APP_API_KEY`: Secret key required by the `/generate-note` endpoint.
- `OPENAI_API_KEY`: Provider API key. Leave empty to use demo mode.
- `OPENAI_BASE_URL`: OpenAI-compatible provider URL.
- `OPENAI_MODEL`: Model identifier.

Use your own secure application key. Never commit `.env` or expose API keys in source code.

## Run the API

```powershell
uvicorn app.main:app --reload
```

API documentation:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health

## Generate a Clinical Note

Send a POST request to `/generate-note` with:

- A valid `X-API-Key` header
- A JSON request matching the `PromptRequest` schema

Use the Swagger UI to inspect the required fields and submit a request.

## Run Tests

```powershell
python -m pytest -v
```

The project currently has 43 passing automated tests.

## Disclaimer

This project is a clinical documentation demonstration, not a diagnostic system. Generated content must be reviewed by a qualified healthcare professional before clinical use.