---
applyTo: "**/*.py"
---

## Context

This instruction file applies to all Python source files. The project uses Python 3.11+ with strict type annotations enforced by `mypy --strict`. All code must pass `ruff format` and `ruff check` with zero warnings. `logging` is mandatory — `print()` is never acceptable in production code. Dependencies are managed via `pyproject.toml` with version pinning.

---

## Coding Standards

- **Python version:** 3.11+ minimum; use `match` expressions, `ExceptionGroup`, `tomllib` where appropriate
- **Type annotations on everything:** All function parameters and return types; `mypy --strict` must pass
- **`logging` not `print()`:** `logging.getLogger(__name__)` in every module; parameterised messages only
- **No bare `except:`:** Always catch a specific exception class; bare `except` masks `SystemExit` and `KeyboardInterrupt`
- **No `import *`:** Explicit imports only — `from module import NameA, NameB`
- **Pydantic or `@dataclass(frozen=True)` for domain objects:** Never raw `dict` as a domain object
- **Constructor injection:** No module-level singleton instances; inject via FastAPI `Depends` or `__init__` parameters
- **`async def` for all I/O:** Never blocking calls (`requests`, `time.sleep`) inside `async def` functions
- **Settings via `BaseSettings`:** All configuration via `pydantic_settings.BaseSettings`; no hardcoded values
- **`pyproject.toml`:** All project metadata, dependencies, and tool config in `pyproject.toml` — no `setup.py`

---

## Preferred Patterns

### Type-Annotated Function

```python
# ✅ CORRECT
import logging
from typing import Sequence

logger = logging.getLogger(__name__)

async def find_orders(customer_id: str, statuses: list[str]) -> Sequence[Order]:
    logger.info("Fetching orders: customer_id=%s, statuses=%s", customer_id, statuses)
    return await order_repo.find_by_customer(customer_id, statuses)

# ❌ WRONG — no annotations, print() instead of logging
def find_orders(customer_id, statuses):
    print(f"Fetching orders for {customer_id}")
    return order_repo.find_by_customer(customer_id, statuses)
```

### Specific Exception Handling

```python
# ✅ CORRECT
try:
    result = await external_service.call(payload)
except ServiceUnavailableError as exc:
    logger.error("External service unavailable", exc_info=True)
    raise DependencyError("Payment service") from exc

# ❌ WRONG — bare except catches SystemExit, KeyboardInterrupt
try:
    result = await external_service.call(payload)
except:
    pass
```

### Pydantic Domain Object

```python
# ✅ CORRECT
from pydantic import BaseModel, field_validator

class OrderId(BaseModel):
    model_config = {"frozen": True}
    value: str

    @field_validator("value")
    @classmethod
    def must_be_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("OrderId must not be empty")
        return v

# ❌ WRONG — raw dict as domain object
def process_order(order: dict) -> dict:
    ...
```

### Settings via BaseSettings

```python
# ✅ CORRECT
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    database_url: str
    secret_key: str
    kafka_bootstrap_servers: str

# ❌ WRONG — hardcoded configuration
DATABASE_URL = "postgresql://user:password@localhost/db"
```

---

## Anti-Patterns — Do NOT Generate

```python
# WRONG: print() instead of logging [BLOCKER]
print(f"Processing order {order_id}")

# WRONG: bare except [BLOCKER]
try:
    do_something()
except:
    pass

# WRONG: import star [MAJOR]
from myapp.models import *

# WRONG: mutable default argument [MAJOR]
def add_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items

# WRONG: blocking I/O in async function [MAJOR]
async def fetch_data(url: str) -> bytes:
    import requests
    return requests.get(url).content  # blocks event loop

# WRONG: module-level singleton (global state) [MAJOR]
db_engine = create_engine(DATABASE_URL)

# WRONG: missing type annotations [MAJOR]
def process(data):
    return data["value"]

# WRONG: Optional.get() equivalent — unguarded attribute access [MINOR]
result = repo.find_by_id(id)
return result.value  # AttributeError if None
```

---

## Dependencies & Versions

| Technology | Version | Notes |
|-----------|---------|-------|
| Python | 3.11+ | Required for `ExceptionGroup`, `tomllib`, improved typing |
| Pydantic | 2.x | `model_config` dict replaces `class Config:` |
| pydantic-settings | 2.x | `BaseSettings` for environment configuration |
| mypy | 1.x | Run with `--strict`; must pass with zero errors |
| Ruff | 0.4+ | Replaces Black + Flake8 + isort; `ruff format` + `ruff check` |
| pytest | 7.x+ | Async tests via `pytest-asyncio`; fixtures over `setUp/tearDown` |
| pytest-asyncio | 0.23+ | `asyncio_mode = "auto"` in `pyproject.toml` |
| httpx | 0.27+ | Async HTTP client; `AsyncClient` for async routes |

---

## Test Conventions

- Use `pytest` with `pytest-asyncio` for async tests — never `unittest.TestCase`
- Mock external dependencies with `unittest.mock.AsyncMock` or `pytest-mock`
- Use `Testcontainers` (via `testcontainers-python`) for database integration tests
- Test file mirrors source: `src/myapp/orders.py` → `tests/test_orders.py`
- One test class per domain class; one test method per behaviour
- Use `pytest.mark.parametrize` for boundary value and equivalence class tests
- Never use `time.sleep()` in tests — use `asyncio.wait_for()` or `anyio.fail_after()`
