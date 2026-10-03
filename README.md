# 🛡️ LLM API Gateway

A high-performance, private, and authenticated LLM API Gateway built with **FastAPI**, **SQLAlchemy 2.0 (Async)**, and **PostgreSQL**. 

This gateway acts as a secure reverse proxy between internal applications (LMS, ERP, CRM) and Large Language Model providers (**Ollama**, **Google Gemini**), exposing an **OpenAI-compatible REST API interface**.

---

## ✨ Features

- **OpenAI Specification Compatibility**: Native support for `/v1/chat/completions` (streaming & tools), `/v1/embeddings`, and `/v1/models` endpoints.
- **Multiple Inference Providers**:
  - **Ollama**: Local and self-hosted models (e.g. `smollm2:135m`, `llama3`).
  - **Google Gemini**: Cloud models via official OpenAI-compatible endpoints (e.g. `gemini-flash-latest`, `text-embedding-004`).
- **Dynamic Database Model Router**:
  - Models are dynamically registered and managed via the `model_configs` table in PostgreSQL.
  - High-performance in-memory TTL cache (60s) ensures near-instantaneous routing with zero database overhead on hot paths.
- **Role-Based Authentication**:
  - **Admin API**: Secured with `X-Secret` for managing client API keys.
  - **Gateway Users**: Secured with `Authorization: Bearer gw_live_...` API keys (stored safely as SHA-256 hashes).
- **Asynchronous Architecture**:
  - Fully non-blocking async architecture built on Python 3.14, `asyncpg`, `httpx`, and connection-pooled SQLAlchemy engines to handle high concurrency seamlessly.

---

## 🛠️ Tech Stack

- **Framework**: FastAPI (Async)
- **Language**: Python 3.14+
- **Database**: PostgreSQL (separate `llm_gateway` production and `llm_gateway_test` test DBs)
- **ORM & Migrations**: SQLAlchemy 2.0 (Async) & Alembic
- **HTTP Client**: HTTPX (Async)
- **Testing**: Pytest & Pytest-Asyncio
- **Package Manager**: `uv`
- **Containers**: Docker & Docker Compose

---

## 📁 Project Structure

```text
llm-gateway/
├── alembic/              # Database migration scripts & env setup
├── app/
│   ├── api/              # API Route Handlers
│   │   └── v1/
│   │       ├── endpoints/# Endpoint handlers (api_keys, chat, embeddings, models)
│   │       └── api_v1.py # Router aggregators (Admin vs Gateway tags)
│   ├── bootstrap/        # App startup modules (routes, docs, middlewares)
│   ├── core/             # Core configurations, Auth, Security, & Dynamic Model Router
│   ├── models/           # SQLAlchemy database entities (ApiKey, ModelConfig)
│   ├── providers/        # Backend provider adapters (BaseLLMProvider, OllamaProvider, GoogleProvider)
│   ├── schemas/          # Pydantic validation schemas (ApiKey, OpenAI specs)
│   ├── tests/            # Automated async pytest suite (PostgreSQL test DB)
│   └── main.py           # Application entrypoint
├── scripts/              # CLI maintenance scripts (seed_models.py)
├── .env                  # Environment configurations
├── compose.yml           # Docker Compose deployment (Gateway + Ollama)
├── Dockerfile.prod       # Production multi-stage Docker build
└── pyproject.toml        # Project dependencies & metadata
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python `>= 3.14`
- [uv package manager](https://github.com/astral-sh/uv) installed
- PostgreSQL database running
- *(Optional)* Local [Ollama](https://ollama.com/) instance running (default: `http://localhost:11434`)
- *(Optional)* [Google AI Studio API Key](https://aistudio.google.com/apikey) for Gemini models

---

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

# Provider Endpoints & Keys
# Use http://localhost:11434 for local host, or http://ollama:11434 inside Docker
OLLAMA_BASE_URL="http://localhost:11434"
GOOGLE_API_KEY="your-google-api-key"
GOOGLE_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai"
```

---

### 3. Run Database Migrations

Apply Alembic migrations to set up the database tables:

```bash
uv run alembic upgrade head
```

---

### 4. Seed Active Models

Populate initial active models into PostgreSQL using the seeder CLI:

```bash
uv run -m scripts.seed_models
```

---

### 5. Start the Application

#### Option A: Local Development
```bash
uv run fastapi dev --port 8000
```

#### Option B: Docker Compose
```bash
docker compose up -d
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

Use your `SECRET_KEY` in the `X-Secret` header to generate a key for a client application:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/api-keys" \
  -H "Content-Type: application/json" \
  -H "X-Secret: your-super-secret-admin-key" \
  -d '{
    "name": "Production App",
    "app_name": "client-app"
  }'
```

**Response**:
```json
{
  "id": "dc5b42bd-069a-4a2a-b74f-83501128d291",
  "name": "Production App",
  "app_name": "client-app",
  "key_prefix": "gw_live_",
  "is_active": true,
  "created_at": "2026-10-04T01:28:38Z",
  "raw_key": "gw_live_abc123secretkey..."
}
```
> ⚠️ **Important**: Save the returned `raw_key` immediately. It is only displayed once!

---

### 2. Listing Available Models (`/api/v1/models`)

Queries the database and returns all active models across all providers:

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/models" \
  -H "Authorization: Bearer gw_live_abc123secretkey..."
```

---

### 3. Chat Completions (`/api/v1/chat/completions`)

Make requests using any OpenAI-compatible SDK or standard cURL with your client API key:

#### Calling Google Gemini:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer gw_live_abc123secretkey..." \
  -d '{
    "model": "gemini-flash-latest",
    "messages": [
      {"role": "user", "content": "Explain API Gateways in 2 sentences."}
    ],
    "temperature": 0.7
  }'
```

#### Calling Ollama:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer gw_live_abc123secretkey..." \
  -d '{
    "model": "smollm2:135m",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

---

### 4. Embeddings (`/api/v1/embeddings`)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/embeddings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer gw_live_abc123secretkey..." \
  -d '{
    "model": "text-embedding-004",
    "input": "Text to embed for vector search"
  }'
```

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
