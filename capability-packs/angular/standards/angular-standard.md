# Angular Engineering Standard

Version: Angular 17+ | TypeScript 5.x | NgRx 18+ | RxJS 7+

---

## Golden Rules (Angular-specific)

| # | Rule | Enforcement |
|---|------|-------------|
| A01 | Standalone components only — no `@NgModule` in new code | Code review |
| A02 | `ChangeDetectionStrategy.OnPush` on every component | post-edit-check hook |
| A03 | `"strict": true` in tsconfig — no `any`, no implicit returns | CI lint |
| A04 | `inject()` over constructor injection in components/directives | Code review |
| A05 | Signals for local state — no `BehaviorSubject` in new code | Code review |
| A06 | `takeUntilDestroyed()` for all subscriptions | post-edit-check hook |
| A07 | Typed reactive forms — `FormGroup<T>` not untyped | Code review |
| A08 | No `console.log` in production code | post-edit-check hook |
| A09 | Lazy-load every feature route | Architecture review |
| A10 | WCAG 2.1 AA accessibility — ARIA labels, keyboard nav | Accessibility audit |

---

## Project Structure

```
src/
├── app/
│   ├── core/                    ← app-wide singletons (auth, http interceptors)
│   │   ├── guards/
│   │   ├── interceptors/
│   │   └── services/
│   ├── shared/                  ← reusable components/pipes/directives
│   │   ├── components/
│   │   ├── directives/
│   │   └── pipes/
│   ├── features/                ← one folder per domain feature
│   │   └── [feature]/
│   │       ├── [feature].routes.ts
│   │       ├── [feature].component.ts
│   │       ├── components/
│   │       ├── services/
│   │       └── store/
│   ├── app.routes.ts
│   └── app.config.ts            ← provideRouter, provideHttpClient, provideAnimations
├── environments/
└── assets/
```

---

## Dependency Injection

```typescript
// ✅ Correct — inject() function
@Component({ standalone: true })
export class UserComponent {
  private readonly userService = inject(UserService);
  private readonly router       = inject(Router);
}

// ❌ Wrong — constructor injection in components
@Component({})
export class UserComponent {
  constructor(private userService: UserService) {}
}
```

Constructor injection is acceptable in **services** for clarity but `inject()` is preferred everywhere.

---

## State Management Decision Tree

```
Local component state (no sharing)
  → signal() + computed()

Shared within a feature (one route subtree)
  → NgRx Signal Store provided in feature routes

App-wide state (auth, config, notifications)
  → NgRx Signal Store provided in root

Complex async + side effects + devtools needed
  → NgRx Feature Store (actions + reducers + effects)
```

---

## HTTP + Error Handling

```typescript
// Use HttpClient with typed generics
getUser(id: string): Observable<User> {
  return this.http.get<User>(`/api/users/${id}`).pipe(
    catchError(err => {
      this.logger.error('Failed to load user', { id, err });
      return throwError(() => new UserNotFoundError(id));
    })
  );
}
```

- Always type HTTP calls: `http.get<User>()` not `http.get()`
- Handle errors in services, not components
- Use interceptors for auth headers and global error logging

---

## Angular Material

- Use `MatDialogRef` with typed result: `MatDialogRef<ConfirmDialogComponent, boolean>`
- Always `closeOnNavigation: true` for dialogs
- Use `MatSnackBar` for user feedback, not `alert()`
- Form fields: always include `mat-error` for validation messages

---

## Build + Performance

```json
// angular.json — production build
"optimization": true,
"sourceMap": false,
"namedChunks": false,
"budgets": [
  { "type": "initial", "maximumWarning": "500kb", "maximumError": "1mb" },
  { "type": "anyComponentStyle", "maximumWarning": "4kb" }
]
```

- Enable `@angular/build` (esbuild) — faster than Webpack
- Defer non-critical images: `<img loading="lazy">`
- Preload key routes: `withPreloading(QuicklinkStrategy)`
- Bundle analysis: `npx nx graph` or `webpack-bundle-analyzer`
