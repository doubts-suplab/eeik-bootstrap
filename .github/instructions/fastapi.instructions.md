---
applyTo: "**/routers/**/*.py, **/routes/**/*.py, **/api/**/*.py, **/main.py, **/app.py"
---

## Context

This instruction file applies to FastAPI application files — routers, schemas, dependencies, middleware, and the application factory. The project uses FastAPI 0.111+ with Pydantic v2 for request/response validation. All routes must be `async def`, return typed Pydantic models, and use RFC 7807 `ProblemDetail` for error responses. OpenAPI documentation is auto-generated; keep schema names meaningful and descriptions accurate.

---

## Coding Standards

- **All routes `async def`:** Never `def` (synchronous) for route handlers — use `async def` with `await`
- **Explicit `response_model=`:** Every route declares `response_model=` and `status_code=`
- **Pydantic v2 schemas:** Request and response models inherit from `pydantic.BaseModel`; use `model_config` for settings
- **`Annotated[T, Depends()]` injection:** Prefer `Annotated` dependency aliases over bare `Depends()` in signatures
- **RFC 7807 errors:** Domain errors translate to `ProblemDetail` (type, title, status, detail, instance); never return raw strings
- **Router organisation:** One `APIRouter` per bounded context; mount routers in `app.py` — no routes in `main.py`
- **Versioned paths:** All routes under `/v{n}/` prefix — e.g. `/v1/orders`
- **`BaseSettings` for config:** No hardcoded URLs, credentials, or feature flags in route code
- **Lifespan events:** Use `@asynccontextmanager` `lifespan` parameter — never deprecated `on_startup`/`on_shutdown`

---

## Preferred Patterns

### Router with Typed Response

```python
# ✅ CORRECT
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_order_service
from app.schemas.orders import CreateOrderRequest, OrderResponse
from app.services.orders import OrderService

router = APIRouter(prefix="/v1/orders", tags=["orders"])

OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(body: CreateOrderRequest, service: OrderServiceDep) -> OrderResponse:
    result = await service.place_order(body.to_command())
    return OrderResponse.from_domain(result)

# ❌ WRONG — synchronous, no response_model, raw dict return
@router.post("/orders")
def create_order(body: dict):
    return {"id": "123"}
```

### RFC 7807 Error Handler

```python
# ✅ CORRECT — global exception handler in app.py
from fastapi import Request
from fastapi.responses import JSONResponse

class DomainError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "https://api.example.com/errors/domain-error",
            "title": "Domain Error",
            "status": exc.status_code,
            "detail": exc.message,
            "instance": str(request.url),
        },
        media_type="application/problem+json",
    )
```

### Pydantic v2 Request/Response Schema

```python
# ✅ CORRECT — Pydantic v2 with model_config
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

class CreateOrderRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    customer_id: str
    items: list[OrderLineItem]
    currency: str = "GBP"

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if v not in {"GBP", "USD", "EUR"}:
            raise ValueError(f"Unsupported currency: {v}")
        return v

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    status: str
    created_at: datetime

    @classmethod
    def from_domain(cls, order: Order) -> "OrderResponse":
        return cls(order_id=str(order.id), status=order.status.value, created_at=order.created_at)
```

### Dependency Injection with Lifespan

```python
# ✅ CORRECT — lifespan manages resource setup/teardown
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await database.connect()
    yield
    # shutdown
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

# ❌ WRONG — deprecated startup/shutdown events
@app.on_event("startup")
async def startup():
    await database.connect()
```

---

## Anti-Patterns — Do NOT Generate

```python
# WRONG: synchronous route handler [BLOCKER]
@router.get("/orders/{order_id}")
def get_order(order_id: str):
    return order_repo.find(order_id)

# WRONG: missing response_model [MAJOR]
@router.post("/orders")
async def create_order(body: dict) -> dict:
    return {"status": "ok"}

# WRONG: returning raw dict from route [MAJOR]
@router.get("/health")
async def health():
    return {"status": "up"}  # Use a typed HealthResponse model

# WRONG: raise HTTPException with plain string detail [MAJOR]
raise HTTPException(status_code=400, detail="Invalid order")  # Use ProblemDetail

# WRONG: global mutable state [MAJOR]
db = AsyncSession()  # module-level; not thread/request safe

# WRONG: hardcoded config [MAJOR]
DATABASE_URL = "postgresql://localhost/orders"

# WRONG: deprecated on_event [MINOR]
@app.on_event("startup")
async def init():
    ...
```

---

## Dependencies & Versions

| Technology | Version | Notes |
|-----------|---------|-------|
| FastAPI | 0.111+ | Annotated dependencies, lifespan parameter |
| Pydantic | 2.x | `model_config = ConfigDict(...)` replaces `class Config:` |
| uvicorn | 0.29+ | ASGI server; run with `--workers` in production |
| SQLAlchemy | 2.x | `async_sessionmaker`; always `await` sessions |
| alembic | 1.13+ | Database migrations; `async` env configuration |
| httpx | 0.27+ | Async HTTP client for downstream calls |
| python-jose | 3.x | JWT decoding; verify `alg`, `aud`, `iss`, `exp` |

---

## Test Conventions

- Use `httpx.AsyncClient` with FastAPI `app` as transport for integration tests — not `TestClient` (synchronous)
- Override dependencies in tests via `app.dependency_overrides`
- Test the full HTTP layer (router → service → repo) in integration tests with `Testcontainers`
- Unit test service logic with mocked repositories using `unittest.mock.AsyncMock`
- Use `pytest.mark.parametrize` for status code boundary tests (200, 201, 400, 404, 422, 500)
- Verify `Content-Type: application/problem+json` on all error responses
