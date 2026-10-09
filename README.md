# Dynamic Prompt Structuring API

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi\&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-Validation-E92063)](https://docs.pydantic.dev/)
[![Tests](https://img.shields.io/badge/Tests-43%20Passed-success)](https://pytest.org/)
[![API](https://img.shields.io/badge/REST-API-blue)](https://fastapi.tiangolo.com/)

A FastAPI-based application that structures dynamic prompts and generates validated clinical notes through an OpenAI-compatible language model API. The project focuses on request validation, prompt construction, API authentication, response validation, and error handling.

## Overview

The Dynamic Prompt Structuring API demonstrates how to build a structured LLM application with clear separation between API routes, prompt engineering, model communication, and output validation.

### Key Features

* **Dynamic prompt construction** — organizes input into structured prompts for clinical note generation.
* **LLM integration** — connects to an OpenAI-compatible API provider.
* **Request validation** — validates incoming data using Pydantic schemas.
* **Response validation** — checks generated clinical note responses before returning them.
* **API key authentication** — protects the note-generation endpoint.
* **Request size protection** — limits incoming request size through custom middleware.
* **Error handling and logging** — handles API and validation errors with structured application logging.
* **Automated testing** — tests API behavior, prompt construction, schemas, and validation logic.
* **Interactive API documentation** — provides Swagger UI through FastAPI.

## Architecture

```text
Client
  |
  v
FastAPI Application
  |
  v
Authentication & Request Size Limit
  |
  v
Request Schema Validation
  |
  v
Dynamic Prompt Builder
  |
  v
LLM Client
  |
  v
Clinical Response Validation
  |
  v
Structured API Response
```

## Tech Stack

| Technology                     | Purpose                         |
| ------------------------------ | ------------------------------- |
| Python                         | Application development         |
| FastAPI                        | REST API framework              |
| Pydantic                       | Request and response validation |
| OpenAI Python SDK              | LLM API communication           |
| Pytest                         | Automated testing               |
| Streamlit                      | User interface                  |
| OpenRouter-compatible endpoint | Language model access           |

## Project Structure

```text
dynamic-prompt-structuring/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── llm_client.py
│   ├── main.py
│   ├── middleware.py
│   ├── prompt_builder.py
│   ├── schemas.py
│   └── validator.py
├── tests/
│   ├── test_api.py
│   ├── test_llm_client.py
│   ├── test_prompt_builder.py
│   ├── test_schemas.py
│   └── test_validation.py
├── ui/
│   └── app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/behra527/dynamic-prompt-structuring-api.git
cd dynamic-prompt-structuring-api
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a reference.

Configure the required settings:

```env
APP_API_KEY=replace-with-a-secure-random-key
OPENAI_API_KEY=your-provider-api-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openrouter/free
```

Replace placeholder values with your own configuration. Use a model identifier supported by your configured provider.

**Security:** Never commit `.env` files, API keys, or other credentials to GitHub.

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

* API base URL: `http://127.0.0.1:8000`
* Swagger documentation: `http://127.0.0.1:8000/docs`
* ReDoc documentation: `http://127.0.0.1:8000/redoc`
* Health endpoint: `http://127.0.0.1:8000/health`

## API Endpoints

| Method | Endpoint         | Purpose                            |
| ------ | ---------------- | ---------------------------------- |
| `GET`  | `/health`        | Check application health           |
| `POST` | `/generate-note` | Generate a validated clinical note |

The `/generate-note` endpoint requires API key authentication. Review the request schema and authentication requirements in Swagger UI at `/docs` before sending a request.

## Running Tests

Run the complete test suite from the project root:

```bash
python -m pytest -v
```

### Test Coverage Areas

* API endpoints and authentication
* LLM client behavior
* Dynamic prompt construction
* Pydantic schema validation
* Clinical response validation

**Latest verified result:** 43 tests passed.

## Security and Reliability

* Keep API credentials in environment variables.
* Validate inputs before processing requests.
* Validate generated outputs before returning them.
* Enforce request size limits.
* Handle provider and validation errors.
* Keep sensitive clinical information out of logs.
* Use HTTPS and appropriate access controls in production.

## Important Disclaimer

This project is a software engineering demonstration for structured clinical note generation. It is not a medical diagnostic system and does not replace qualified clinical judgment. Generated content must be reviewed by an authorized healthcare professional before clinical use. Do not submit real patient information unless the deployment has appropriate privacy, security, and regulatory safeguards.

## Future Improvements

* Add continuous integration for automated testing.
* Expand integration and end-to-end test coverage.
* Add structured observability and request tracing.
* Introduce configurable model and prompt profiles.
* Improve deployment and production security documentation.

