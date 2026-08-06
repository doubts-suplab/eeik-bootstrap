# Go Engineering Standard

**Applies To:** All Go projects
**Targets:** Go 1.22+ · standard-library-first · cloud-native services

---

## Golden Rules (Go)

| Rule | Implementation |
|---|---|
| `gofmt` + `go vet` + `golangci-lint` clean | Enforced in CI; formatting is not a review topic |
| Accept interfaces, return structs | Interfaces defined at the consumer, kept small (1–3 methods) |
| Errors are values, always wrapped | `fmt.Errorf("doing X: %w", err)`; classify with `errors.Is` / `errors.As` |
| `context.Context` is the first argument | On every I/O, RPC, and DB call; propagate cancellation + deadlines |
| Explicit dependency wiring | Constructors (`New...`); no package-level mutable globals |
| Structured logging via `log/slog` | Key/value attrs; never `fmt.Println` in service code |
| Table-driven tests | Subtests via `t.Run`; `t.Parallel()` where independent |
| Parameterised SQL only | `$1` / `?` placeholders; never string-concatenated queries |
| Bounded goroutines | Every goroutine owned + cancellable (`context`, `errgroup`, `WaitGroup`) |

## Project Layout

```
cmd/<service>/main.go        # wiring only — build the dependency graph, start the server
internal/<domain>/           # domain types + business logic (no framework imports)
internal/<domain>/http/      # transport adapter (handlers, routing)
internal/<domain>/store/     # persistence adapter (repository impls)
internal/platform/           # cross-cutting: config, logging, telemetry
```

`internal/` keeps the API surface private; the domain package never imports transport or store.

## Error Handling

```go
var ErrNotFound = errors.New("not found")

func (s *Store) Get(ctx context.Context, id string) (Order, error) {
    var o Order
    err := s.db.QueryRowContext(ctx, `SELECT id, status FROM orders WHERE id = $1`, id).
        Scan(&o.ID, &o.Status)
    if errors.Is(err, sql.ErrNoRows) {
        return Order{}, fmt.Errorf("order %s: %w", id, ErrNotFound)
    }
    if err != nil {
        return Order{}, fmt.Errorf("query order %s: %w", id, err)
    }
    return o, nil
}
```

Handlers map sentinel errors to status codes — never leak internal errors to clients verbatim.

## Testing

- Table-driven, deterministic, no `time.Sleep` — inject a clock; use `context` timeouts.
- Fakes over mocks where a small in-memory implementation is clearer.
- `go test -race ./...` in CI — the race detector is mandatory for concurrent code.
- Integration tests use Testcontainers-go for real Postgres/Kafka; tag with `//go:build integration`.

## Concurrency

- Prefer `errgroup.Group` for fan-out with error propagation and cancellation.
- Channels for ownership transfer; mutexes for protecting state — don't mix the two for one datum.
- Never leak a goroutine: it must return when its `context` is cancelled.

## Observability

- `log/slog` structured logs with a request/trace ID attribute.
- OpenTelemetry traces across service boundaries; Prometheus metrics on a separate internal port.
- Health endpoints: `/healthz` (liveness) and `/readyz` (readiness, checks dependencies).

## Anti-Patterns (Reject in Review)

- `panic` for expected errors; ignored errors (`_ =`) without a justifying comment.
- Business logic in `main`; package-level mutable globals.
- Unbounded goroutines; `time.Sleep` in tests; string-concatenated SQL.
- `interface{}`/`any` where a concrete or generic type fits.
- Public `/debug/pprof` or `/metrics` on the client-facing listener.
