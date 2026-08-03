# 🛡️ LLM API Gateway

A high-performance, private, and authenticated LLM API Gateway built with **FastAPI**, **SQLAlchemy 2.0 (Async)**, and **PostgreSQL**. 

This gateway acts as a secure reverse proxy between internal applications (LMS, ERP, CRM) and local or cloud-based Large Language Model backends (such as **Ollama**), providing an **OpenAI-compatible REST API interface**.

---

## ✨ Features

- **OpenAI Specification Compatibility**: Native support for `/v1/chat/completions`, `/v1/embeddings`, and `/v1/models` endpoints.
- **Secure API Key Management**:
  - SHA-256 hashed storage (raw keys are generated once with prefix `gw_live_...` and never saved in plain text).
  - Protected Administrative CRUD API for key creation and revocation via `X-Admin-Secret`.
- **Pluggable Model Router**:
  - Centralized routing dispatcher resolving requested models to appropriate inference providers (e.g. Ollama).
- **Asynchronous Architecture**:
  - Fully non-blocking standard built on Python 3.14, `asyncpg`, `httpx`, and loop-cached SQLAlchemy engines to handle high concurrency seamlessly.

---

## 🛠️ Tech Stack

- **Framework**: FastAPI (Async)
- **Language**: Python 3.14+
- **Database**: PostgreSQL (separate `llm_gateway` production and `llm_gateway_test` test DBs)
- **ORM & Migrations**: SQLAlchemy 2.0 (Async) & Alembic
- **HTTP Client**: HTTPX (Async)
- **Testing**: Pytest & Pytest-Asyncio
- **Package Manager**: `uv`

---

## 📁 Project Structure

```text
llm-gateway/
├── alembic/              # Database migration scripts & env setup
├── app/
│   ├── api/              # API Route Handlers
│   │   └── v1/
│   │       ├── endpoints/# Endpoint handlers (api_keys, chat, embeddings, models)
│   │       └── api_v1.py # Router aggregators
│   ├── bootstrap/        # App startup modules (routes, docs, middlewares)
│   ├── core/             # Core configurations, Auth, Security, & Model Router
│   ├── models/           # SQLAlchemy database entities (ApiKey, ModelConfig)
│   ├── providers/        # Backend provider adapters (BaseLLMProvider, OllamaProvider)
│   ├── schemas/          # Pydantic validation schemas (ApiKey, OpenAI specs)
│   ├── tests/            # Automated async pytest suite (PostgreSQL test DB)
│   └── main.py           # Application entrypoint
├── .env                  # Environment configurations
├── alembic.ini           # Alembic settings
└── pyproject.toml        # Project dependencies & metadata
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python `>= 3.14`
- [uv package manager](https://github.com/astral-sh/uv) installed
- PostgreSQL database running locally or remotely
- Local [Ollama](https://ollama.com/) instance running (default: `http://localhost:11434`)

### 2. Environment Setup

Create a `.env` file in the root directory:

```ini
APP_NAME="LLM API Gateway"
APP_ENV=development
DEBUG=True
SECRET_KEY="your-super-secret-admin-key"

# Database Configuration
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/llm_gateway"
TEST_DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/llm_gateway_test"

# Model Provider Endpoints
OLLAMA_BASE_URL="http://localhost:11434"
```

### 3. Run Database Migrations

Apply Alembic migrations to set up database tables:

```bash
uv run alembic upgrade head
```

### 4. Start the Application

Run the server using Uvicorn:

```bash
uv run uvicorn app.main:app --reload
```

Interactive API Documentation will be live at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/health`

---

## 🧪 Running Automated Tests

Run the full async test suite against the dedicated PostgreSQL test database (`llm_gateway_test`):

```bash
uv run pytest
```

---

## 📖 API Usage Guide

### 1. Generating a Client API Key (Admin Endpoint)

Use your `SECRET_KEY` in the `X-Admin-Secret` header to generate a key for an internal service:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/api-keys" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Secret: your-super-secret-admin-key" \
  -d '{
    "name": "LMS Backend Production",
    "app_name": "lms"
  }'
```

**Response**:
```json
{
  "id": "dc5b42bd-069a-4a2a-b74f-83501128d291",
  "name": "LMS Backend Production",
  "app_name": "lms",
  "key_prefix": "gw_live_",
  "is_active": true,
  "created_at": "2026-08-04T01:28:38.366016Z",
  "raw_key": "gw_live_abc123secretkey..."
}
```
> ⚠️ **Important**: Save the returned `raw_key` immediately. It is only displayed once!

---

### 2. Chat Completions (`/api/v1/chat/completions`)

Make requests using any OpenAI-compatible SDK or standard cURL with your client API key:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer gw_live_abc123secretkey..." \
  -d '{
    "model": "gemma4",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain API Gateways in 2 sentences."}
    ],
    "temperature": 0.7
  }'
```

---

### 3. Embeddings (`/api/v1/embeddings`)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/embeddings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer gw_live_abc123secretkey..." \
  -d '{
    "model": "vector-model",
    "input": "Text to embed for vector search"
  }'
```

---

### 4. Listing Available Models (`/api/v1/models`)

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/models" \
  -H "Authorization: Bearer gw_live_abc123secretkey..."
```

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
