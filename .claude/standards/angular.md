# Angular Coding Standards

> Mandatory standards for all Angular TypeScript/HTML/SCSS code. Enforced by `angular-developer`, `angular-tester`, and `code-reviewer` agents.

---

## Framework Version & Configuration

- **Angular 17+** with **standalone components** (no NgModules unless migrating legacy)
- **TypeScript strict mode** (`"strict": true` in `tsconfig.json`) — no `any`, no `!` non-null assertions
- **`ChangeDetectionStrategy.OnPush`** on all components
- **Signals API** for reactive state (`signal()`, `computed()`, `effect()`)
- RxJS 7+ for async streams; prefer signals for component state

---

## Component Structure

```typescript
@Component({
  selector: 'app-order-list',
  standalone: true,
  imports: [CommonModule, RouterModule, OrderCardComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @for (order of orders(); track order.id) {
      <app-order-card [order]="order" />
    }
  `,
  styleUrl: './order-list.component.scss',
})
export class OrderListComponent implements OnInit {
  private readonly orderService = inject(OrderService);

  orders = signal<Order[]>([]);
  isLoading = signal(false);
  error = signal<string | null>(null);

  ngOnInit(): void {
    this.loadOrders();
  }

  private loadOrders(): void {
    this.isLoading.set(true);
    this.orderService.getOrders()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (orders) => this.orders.set(orders),
        error: (err) => this.error.set(err.message),
        complete: () => this.isLoading.set(false),
      });
  }
}
```

---

## Dependency Injection

- Use `inject()` function — not constructor parameter injection
- Mark services as `providedIn: 'root'` unless scoped injection is required
- Use `DestroyRef` with `takeUntilDestroyed()` for subscription cleanup

---

## Template Standards

- Use Angular 17 control flow syntax (`@if`, `@for`, `@switch`) — not `*ngIf`, `*ngFor`
- Always provide `track` expression in `@for` loops
- Avoid logic in templates — derive display values in computed signals or pipe transforms
- Use `async` pipe only for Observables not already converted to signals

---

## Forms

- **Reactive forms** (`ReactiveFormsModule`) for all non-trivial forms
- Template-driven forms only for simple, single-field forms
- Define form group types explicitly — no untyped `FormGroup`
- Validate with built-in validators + custom `ValidatorFn` — no ad-hoc validation in components

---

## Services

```typescript
@Injectable({ providedIn: 'root' })
export class OrderService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api/v1/orders';

  getOrders(): Observable<Order[]> {
    return this.http.get<Order[]>(this.baseUrl).pipe(
      catchError(this.handleError),
    );
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    return throwError(() => new Error(error.error?.detail ?? 'An error occurred'));
  }
}
```

---

## Routing

- Lazy-load all feature routes with `loadComponent()` — never eagerly import feature components in the root router
- Use `CanActivateFn` (functional guard) — not class-based guards
- Define typed route parameters with `withComponentInputBinding()`

---

## SCSS Standards

- Use BEM naming convention for component CSS classes
- Component styles are scoped (`encapsulation: ViewEncapsulation.Emulated` default)
- Use CSS custom properties (variables) for design tokens — no magic colour/size values
- No global styles except design token definitions in `styles.scss`

---

## Testing Standards

- Jasmine + Karma + Istanbul
- All components tested with `TestBed` and `ComponentFixture`
- Mock services with `jasmine.createSpyObj` — do not use real HTTP
- Test `OnPush` components with explicit `fixture.detectChanges()` after signal updates
- Coverage minimum: 80% statements, 70% branches (enforced by Istanbul/karma-coverage)
- Never use `jasmine.clock()` — use `fakeAsync` with `tick()` for timer control
