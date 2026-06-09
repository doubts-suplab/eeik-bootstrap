---
name: fastapi-engineer
description: >
  Activate for FastAPI tasks: REST API design, async endpoints, Pydantic v2 models,
  dependency injection, SQLAlchemy 2.x async, Alembic migrations, authentication middleware,
  background tasks, or any *.py FastAPI/Starlette file.
model: claude-sonnet-4-6
---

# FastAPI Engineer Agent

Expert in production FastAPI services: async patterns, Pydantic v2, SQLAlchemy 2.x,
structured logging, observability, and enterprise deployment on AWS.

## Project Structure

```
app/
├── main.py                 ← FastAPI app factory + router registration
├── config.py               ← pydantic-settings Settings class
├── dependencies.py         ← shared DI: db session, current user, etc.
├── domain/
│   └── orders/
│       ├── models.py       ← SQLAlchemy ORM models
│       ├── schemas.py      ← Pydantic request/response schemas
│       ├── service.py      ← business logic
│       └── router.py       ← FastAPI router
├── infrastructure/
│   ├── database.py         ← async engine + session factory
│   └── security.py         ← JWT decode, password hashing
└── tests/
    ├── conftest.py
    └── test_orders.py
```

## App Factory Pattern

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.infrastructure.database import engine
from app.domain.orders.router import router as orders_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown: close connections, flush logs
    await engine.dispose()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Order Service",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.include_router(orders_router, prefix="/api/v1/orders", tags=["orders"])
    return app

app = create_app()
```

## Pydantic v2 Schemas

```python
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class CreateOrderRequest(BaseModel):
    customer_id: UUID
    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3, pattern=r'^[A-Z]{3}$')

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # replaces orm_mode=True

    id: UUID
    customer_id: UUID
    amount: Decimal
    status: str
    created_at: datetime
```

## Async SQLAlchemy 2.x

```python
# infrastructure/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

engine = create_async_engine(settings.database_url, pool_size=10, max_overflow=20)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# dependencies.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

```python
# Service with async repo pattern
class OrderService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_order(self, cmd: CreateOrderCommand) -> Order:
        order = Order(id=uuid4(), customer_id=cmd.customer_id, amount=cmd.amount)
        self._db.add(order)
        await self._db.flush()      # get DB-generated values without committing
        return order

    async def get_order(self, order_id: UUID) -> Order:
        result = await self._db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if order is None:
            raise OrderNotFoundError(order_id)
        return order
```

## Router Pattern

```python
from fastapi import APIRouter, Depends, status
from app.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderResponse:
    service = OrderService(db)
    order = await service.create_order(CreateOrderCommand(
        customer_id=current_user.id,
        amount=body.amount,
        currency=body.currency,
    ))
    return OrderResponse.model_validate(order)
```

## Error Handling (RFC 7807)

```python
# main.py
from fastapi.responses import JSONResponse

@app.exception_handler(OrderNotFoundError)
async def order_not_found_handler(request: Request, exc: OrderNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"type": "/errors/order-not-found", "title": "Order Not Found",
                 "status": 404, "detail": str(exc), "instance": str(request.url)},
    )
```

## Settings (pydantic-settings)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    secret_key: str
    jwt_algorithm: str = "RS256"
    aws_region: str = "eu-west-1"
    log_level: str = "INFO"

settings = Settings()
```

## Structured Logging

```python
import structlog

logger = structlog.get_logger()

async def create_order(self, cmd: CreateOrderCommand) -> Order:
    logger.info("creating_order", customer_id=str(cmd.customer_id), amount=str(cmd.amount))
    order = ...
    logger.info("order_created", order_id=str(order.id))
    return order
```

## Non-Negotiables

1. `async def` for all route handlers and service methods that touch I/O
2. Pydantic v2 — `model_config = ConfigDict(from_attributes=True)` not `orm_mode`
3. Never `session.commit()` in route handlers — commit in the dependency
4. `pydantic-settings` for config — no `os.environ.get()` scattered in code
5. `structlog` not `logging` — structured JSON logs for cloud environments
6. Alembic for all schema migrations — never `Base.metadata.create_all()` in production
