# Python Engineering Standard

**Applies To:** All Python projects  
**Framework Targets:** FastAPI 0.110+, Python 3.12+

---

## Golden Rules (Python)

| Rule | Implementation |
|------|---------------|
| Type hints everywhere | All function signatures annotated; Pydantic for data models |
| Pydantic for validation | Request/response models are `BaseModel` subclasses |
| Dependency injection via FastAPI `Depends()` | No global state; no module-level singletons |
| Async by default | `async def` for all endpoint handlers and I/O operations |
| `structlog` for logging | Never `print()`; structured JSON logs |
| `python-dotenv` + `pydantic-settings` for config | No hardcoded config values |
| `pytest` + `pytest-asyncio` for tests | Minimum 80% coverage |
| `ruff` for linting and formatting | PEP 8, enforced in CI |
| No mutable default arguments | `def f(items: list = None)` → `def f(items: list | None = None)` |

---

## Project Structure

```
src/{service}/
├── main.py                    ← FastAPI app factory (not top-level)
├── domain/
│   ├── models/                ← Pydantic domain models (no ORM)
│   ├── repositories/          ← Repository interfaces (ABC)
│   └── events/                ← Domain events (dataclasses)
├── application/
│   ├── use_cases/             ← Use case functions / classes
│   └── dtos/                  ← Request/response DTOs (Pydantic)
├── infrastructure/
│   ├── persistence/           ← SQLAlchemy models + repo implementations
│   ├── messaging/             ← Event publishers (SQS/SNS/Kafka)
│   └── config/
│       └── settings.py        ← pydantic-settings BaseSettings
└── api/
    ├── routes/                ← FastAPI routers (one per resource)
    ├── dependencies/          ← FastAPI dependency providers
    └── middleware/            ← Custom middleware
```

---

## FastAPI Patterns

### Settings (pydantic-settings)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
    database_url: str
    aws_region: str = "eu-west-1"
    log_level: str = "INFO"

settings = Settings()  # reads from env/secrets at startup
```

### Dependency Injection

```python
from functools import lru_cache
from fastapi import Depends

@lru_cache
def get_settings() -> Settings:
    return Settings()

def get_order_service(
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> OrderService:
    repo = SqlAlchemyOrderRepository(db)
    return OrderService(repo)

@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    request: CreateOrderRequest,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    result = await service.create_order(request)
    return OrderResponse.model_validate(result)
```

### Error Handling (RFC 7807)

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "type": f"https://errors.example.com/{exc.error_code}",
            "title": exc.title,
            "detail": exc.message,
            "instance": str(request.url),
        },
    )
```

---

## Testing Standards

```python
# ✅ Async test with pytest-asyncio
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_order_returns_201(async_client: AsyncClient) -> None:
    response = await async_client.post("/orders", json={
        "customer_id": "3fa85f64",
        "items": [{"product_id": "abc", "quantity": 2}],
    })
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"

# ✅ Testcontainers for integration tests
@pytest.fixture(scope="session")
def postgres_container():
    with PostgreSqlContainer("postgres:15") as container:
        yield container
```
