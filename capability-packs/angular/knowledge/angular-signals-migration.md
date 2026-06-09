# Angular Signals Migration Pattern

**Type**: Migration Pattern  
**Applicability**: Angular 16 → 17+ codebases moving from RxJS-only to Signals

---

## Context

Angular 16 introduced Signals as a reactive primitive. Angular 17–18 made them the
recommended approach for local component state. Many enterprise codebases still use
`BehaviorSubject` everywhere. This pattern guides the migration.

---

## Migration Mapping

| Old (RxJS) | New (Signals) | Notes |
|---|---|---|
| `BehaviorSubject<T>(init)` | `signal<T>(init)` | Local state |
| `subject.asObservable()` | `signal.asReadonly()` | Read-only exposure |
| `subject.next(val)` | `signal.set(val)` | Update |
| `combineLatest([a$, b$])` | `computed(() => [a(), b()])` | Derived state |
| `tap(() => doSomething())` | `effect(() => doSomething())` | Side effects |
| `async` pipe in template | Direct `signal()` call | No pipe needed |
| `takeUntil(destroy$)` | `takeUntilDestroyed()` | Subscription cleanup |

---

## Step-by-step Migration

### 1. Local component state (safe to migrate immediately)

```typescript
// BEFORE
export class CounterComponent {
  private count$ = new BehaviorSubject(0);
  displayCount$ = this.count$.asObservable();
  increment() { this.count$.next(this.count$.value + 1); }
}

// AFTER
export class CounterComponent {
  count = signal(0);
  increment() { this.count.update(c => c + 1); }
  // template: {{ count() }} — no async pipe
}
```

### 2. Derived state

```typescript
// BEFORE
total$ = combineLatest([price$, qty$]).pipe(map(([p, q]) => p * q));

// AFTER
total = computed(() => this.price() * this.qty());
```

### 3. Async data from HTTP (keep Observable, bridge with toSignal)

```typescript
// Service stays Observable — don't change services
// Component bridges with toSignal
export class UserListComponent {
  private userService = inject(UserService);
  users = toSignal(this.userService.getAll(), { initialValue: [] });
  // template: @for (user of users(); track user.id)
}
```

### 4. Input signals (Angular 17.1+)

```typescript
// BEFORE
@Input() user!: User;

// AFTER
user = input.required<User>();       // required input
theme = input<'light' | 'dark'>('light');  // optional with default
```

### 5. Output events (Angular 17.3+)

```typescript
// BEFORE
@Output() selected = new EventEmitter<User>();

// AFTER
selected = output<User>();
// emit: this.selected.emit(user)
```

---

## What NOT to Migrate

- **Services** — keep returning `Observable<T>` for HTTP; services are consumed by
  multiple components and some need the full RxJS power (retry, debounce, etc.)
- **Complex async sequences** — `switchMap`, `mergeMap`, `forkJoin` chains stay as RxJS
- **NgRx Effects** — these are inherently Observable-based; keep them
- **Shared state across components** — use NgRx Signal Store, not raw signals

---

## Anti-Pattern: Signal in Service (wrong)

```typescript
// ❌ Don't expose raw signals from services
@Injectable({ providedIn: 'root' })
export class UserService {
  users = signal<User[]>([]);  // WRONG — internal implementation leaks
}

// ✅ Service returns Observable, component converts with toSignal
@Injectable({ providedIn: 'root' })
export class UserService {
  getAll(): Observable<User[]> { return this.http.get<User[]>('/api/users'); }
}
```

---

## Migration Order

1. New features: use Signals from the start
2. Existing components: migrate on touch (when you edit the component anyway)
3. Shared/reusable components: migrate in a dedicated sprint (high leverage)
4. Services: do NOT migrate HTTP services; only migrate services with pure local state
