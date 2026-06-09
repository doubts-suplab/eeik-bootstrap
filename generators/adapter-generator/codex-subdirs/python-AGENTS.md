# AGENTS.md — Python Source Directory

> **Deploy to**: `python/AGENTS.md` or the root of your Python project
> Codex CLI reads this when working in Python files.

---

You are working in a **Python service** (FastAPI or data pipeline).

## Stack

- Python 3.12+
- FastAPI + Pydantic v2 (for services)
- PySpark + AWS Glue / Databricks (for data pipelines)
- SQLAlchemy 2.x async (for services with relational DB)
- `structlog` for structured logging
- `ruff` for linting; `mypy` for type checking
- `pytest` + `pytest-asyncio` for tests

## Non-Negotiable Rules

1. **Type hints everywhere** — every function parameter and return type annotated
2. **Pydantic v2 for data models** — `model_config = ConfigDict(...)` not `class Config:`
3. **`structlog` not `logging`** — `logger.info("event", key=value)` structured fields
4. **`pydantic-settings` for config** — never `os.environ.get()` scattered in code
5. **`async def` for all I/O** — FastAPI routes and service methods that touch DB/network
6. **Never `SELECT *`** — explicit columns in all SQLAlchemy queries
7. **No hardcoded secrets** — use environment variables or AWS Secrets Manager
8. **`BigDecimal` equivalent** — use `Decimal` from Python `decimal` module for money
9. **Idempotent pipelines** — data jobs must be re-runnable without creating duplicates
10. **Dead-letter handling** — failed records go to DLQ/error table, never silently dropped

## Project Structure (FastAPI Service)

```
app/
├── main.py             ← FastAPI app factory + lifespan
├── config.py           ← pydantic-settings Settings
├── dependencies.py     ← DI: db session, current user
├── domain/
│   └── {feature}/
│       ├── models.py   ← SQLAlchemy ORM models
│       ├── schemas.py  ← Pydantic request/response
│       ├── service.py  ← Business logic
│       └── router.py   ← FastAPI router
└── infrastructure/
    └── database.py     ← async engine + session factory
```

## Key Patterns

```python
# Pydantic v2 schema
class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    amount: Decimal

# Structlog usage
logger = structlog.get_logger()
logger.info("order_created", order_id=str(order.id), amount=str(order.amount))

# Settings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    database_url: str
    aws_region: str = "eu-west-1"
```

## Testing Standards

```python
# pytest-asyncio for async tests
@pytest.mark.asyncio
async def test_create_order(async_client: AsyncClient):
    response = await async_client.post("/api/v1/orders", json={"amount": "10.00"})
    assert response.status_code == 201
    assert response.json()["status"] == "PLACED"
```

- Use `pytest-asyncio` for async test functions
- Use `httpx.AsyncClient` for FastAPI integration tests
- Use `testcontainers-python` for real DB in integration tests
- Coverage target: 80%
