# Contributing to LLM API Gateway

Thank you for your interest in contributing to **LLM API Gateway**! Contributions from the community help make this project better for everyone.

---

## 🛠️ Development Setup

1. **Fork & Clone**
   ```bash
   git clone https://github.com/<your-username>/llm-gateway.git
   cd llm-gateway
   ```

2. **Install Dependencies**
   Ensure you have [uv](https://github.com/astral-sh/uv) installed.
   ```bash
   uv sync
   ```

3. **Configure Environment**
   Copy `.env.example` to `.env` and configure your local PostgreSQL database & Ollama instance:
   ```bash
   cp .env.example .env
   ```

4. **Run Migrations**
   ```bash
   uv run alembic upgrade head
   ```

5. **Run the Development Server**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

---

## 🧪 Running Tests

Ensure all automated tests pass before submitting a Pull Request:

```bash
uv run pytest
```

---

## 📝 Pull Request Guidelines

- Ensure your code follows PEP 8 formatting rules.
- Add clear commit messages describing your changes.
- Add unit or integration tests for new features/bug fixes.
- Update documentation or `README.md` if your changes alter configuration or endpoints.
