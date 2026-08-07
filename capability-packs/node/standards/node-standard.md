# Node.js / TypeScript Engineering Standard

**Applies To:** All Node.js backend projects
**Targets:** Node 20+ · TypeScript 5.5+ (`strict`) · NestJS 10 / Fastify 4 · Vitest

---

## Golden Rules (Node / TypeScript)

| Rule | Implementation |
|---|---|
| `"strict": true`, no `any` | Use `unknown` + narrowing or Zod; `noUncheckedIndexedAccess` on |
| Validate every boundary | Zod parses request bodies, query params, and env vars |
| Explicit DI | NestJS providers / a DI container; no mutable module-level singletons |
| No floating promises | `await` or explicit `void`; ESLint `no-floating-promises` enforced |
| Typed errors → status codes | Domain error classes mapped by an exception filter / error handler |
| Structured logging | `pino` or Nest `Logger` with fields; never `console.log` in service code |
| Parameterised queries | Prisma / Drizzle / parameterised SQL; never string-concatenated queries |
| Fast, isolated tests | Vitest/Jest; deterministic; fakes over deep mocks; Testcontainers for integration |

## Project Layout (NestJS-style, applies to Fastify too)

```
src/
  main.ts                 # bootstrap only — build the app, start the server
  <module>/
    <module>.controller.ts  # interface layer — HTTP, validation (Zod)
    <module>.service.ts     # application layer — use cases
    <module>.repository.ts  # infrastructure — persistence
    dto/ schema.ts          # Zod schemas + inferred types
  common/                 # cross-cutting: config, logging, filters, guards
```

The domain/service layer must not import HTTP or ORM types — depend on interfaces.

## Configuration

```ts
const Env = z.object({
  DATABASE_URL: z.string().url(),
  PORT: z.coerce.number().default(8080),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
});
export const env = Env.parse(process.env);   // fail fast at startup on bad config
```

Never read `process.env` outside this module. No secrets in the repo — inject at runtime.

## Error Handling

```ts
export class NotFoundError extends Error {
  constructor(public readonly resource: string, public readonly id: string) {
    super(`${resource} ${id} not found`);
  }
}
// An exception filter maps NotFoundError → 404 Problem Details; unknown errors → 500 (no stack leak).
```

## Testing

- Vitest (or Jest) with `--coverage`; minimum 80% lines on business logic.
- No real network in unit tests; mock at the port boundary.
- Integration tests use Testcontainers for real Postgres/Redis; tag and run separately in CI.
- No `setTimeout`-based waits — use fake timers or awaited conditions.

## Observability

- `pino` structured logs with a correlation ID via async local storage.
- OpenTelemetry auto-instrumentation for HTTP + DB; `/metrics` on a separate internal port.
- `/healthz` (liveness) + `/readyz` (readiness) endpoints.

## Anti-Patterns (Reject in Review)

- `any`; floating promises; `console.log` in service code.
- Direct `process.env` access in business code; secrets in source.
- String-concatenated queries; business logic in `main.ts`.
- Deep mock chains that assert on implementation rather than behaviour.
- Mutable module-level singletons standing in for dependency injection.
