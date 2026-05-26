---
mode: "ask"
description: "Generate an Angular HttpClient service with typed models and a spec file"
---

## Objective

Generate a complete Angular service that communicates with a REST API using `HttpClient`, with fully typed request/response models, error handling, and a companion spec file using `HttpTestingController`.

---

## Instructions to Copilot

1. **Service class** (`{name}.service.ts`):
   - `@Injectable({ providedIn: 'root' })`
   - Use `inject(HttpClient)` — not constructor injection
   - Every method returns a typed Observable: `Observable<Customer[]>`, `Observable<Customer>`, `Observable<void>`
   - Use `HttpParams` for query parameters — never build query strings manually
   - Add `catchError` with a typed error handler that transforms `HttpErrorResponse` into a domain error
   - Add `map` operators to transform raw API responses if the API shape differs from the domain model
   - Use `shareReplay(1)` on data streams that multiple components will subscribe to

2. **TypeScript Models** (in `{name}.model.ts` or co-located):
   - Define `interface` types for request and response shapes
   - Use `readonly` fields on response interfaces — API responses should not be mutated
   - Define enums or union types for status fields: `type OrderStatus = 'PENDING' | 'CONFIRMED' | 'CANCELLED'`

3. **Spec file** (`{name}.service.spec.ts`):
   - Configure `TestBed` with `HttpClientTestingModule`
   - Inject `HttpTestingController`
   - Call `httpMock.verify()` in `afterEach`
   - Test every service method:
     - Verify the HTTP method and URL
     - Verify query parameters if applicable
     - Flush a mock response and assert the emitted value
     - Flush an error response and assert the error is handled

---

## Input

Provide:
- **Service name** — e.g., "Customer", "Order"
- **Base API URL** — e.g., `/api/v1/customers`
- **Operations** — list each operation: get all, get by ID, create, update, delete
- **Request/response fields** — the data model fields for each operation
- **Error handling** — how should HTTP errors be surfaced? (throw, emit null, return empty array)

---

## Output

Three files:

1. `src/app/features/{feature}/{name}.model.ts`
2. `src/app/features/{feature}/{name}.service.ts`
3. `src/app/features/{feature}/{name}.service.spec.ts`

---

## Quality Gates

- [ ] All `HttpClient` calls have explicit type parameters
- [ ] No `any` types in the service or models
- [ ] `HttpParams` used for query parameters
- [ ] `catchError` present on at least the main data-fetching methods
- [ ] Response models use `readonly` fields
- [ ] Spec file calls `httpMock.verify()` in `afterEach`
- [ ] Each spec test asserts on both the HTTP call made and the emitted value
