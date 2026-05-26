---
mode: "ask"
description: "Generate a standalone Angular component with template, styles, and spec file"
---

## Objective

Generate a complete, standalone Angular component with its HTML template, SCSS stylesheet, and Jasmine spec file. The component follows Angular 15+ standalone conventions with `OnPush` change detection, Signals API where applicable, and BEM-named styles.

---

## Instructions to Copilot

Generate the following files for the described component:

1. **Component TypeScript** (`{name}.component.ts`):
   - `standalone: true`, `changeDetection: ChangeDetectionStrategy.OnPush`
   - Use `inject()` for service injection — not constructor parameters
   - Use `signal()` for local reactive state, `computed()` for derived values
   - Use `input()` for required/optional inputs (Angular 17+) or `@Input()` for 15/16
   - Use `output()` for events (Angular 17+) or `@Output() EventEmitter` for 15/16
   - Import only what is needed in `imports: []`
   - Subscribe to Observables via `async` pipe in template, not in the component class
   - Apply `takeUntilDestroyed(this.destroyRef)` if manual subscription is unavoidable

2. **HTML Template** (`{name}.component.html`):
   - Use Angular 17+ control flow syntax: `@if`, `@for`, `@switch` (or `*ngIf`, `*ngFor` for <17)
   - `@for` (or `*ngFor`) must always include `track` (or `trackBy`)
   - Interactive elements must have `aria-*` attributes or accessible labels
   - Use CSS class binding `[ngClass]` — never inline `[style]` bindings
   - Reference template variables from the component using signals: `{{ customers() }}`

3. **SCSS** (`{name}.component.scss`):
   - BEM naming: `.{component-name}__element--modifier`
   - Use CSS custom properties (`var(--spacing-sm)`) for spacing and colours — no hardcoded values
   - No global styles — only styles scoped to this component
   - Mobile-first responsive breakpoints if the component renders a list or grid

4. **Spec file** (`{name}.component.spec.ts`):
   - `TestBed.configureTestingModule` with `imports: [ComponentUnderTest]`
   - Mock all injected services with `jasmine.createSpyObj`
   - Test rendered output via `fixture.nativeElement.querySelector`
   - Test that `@Input` bindings change rendered output
   - Test that `@Output` events emit correctly
   - Call `fixture.detectChanges()` after any state mutation
   - Name tests: `it('should ...', ...)`

---

## Input

Provide:
- **Component name** — e.g., "CustomerList", "OrderDetail", "InvoiceForm"
- **Purpose** — what does the component display or allow the user to do?
- **Inputs** — what data does it receive from a parent component?
- **Outputs** — what events does it emit?
- **Services needed** — which Angular services does it inject?
- **Angular version** — 15, 16, or 17+ (for control flow syntax)

---

## Output

Four files, each with their path:

1. `src/app/features/{feature}/{name}.component.ts`
2. `src/app/features/{feature}/{name}.component.html`
3. `src/app/features/{feature}/{name}.component.scss`
4. `src/app/features/{feature}/{name}.component.spec.ts`

---

## Quality Gates

- [ ] `standalone: true` and `changeDetection: ChangeDetectionStrategy.OnPush`
- [ ] `inject()` used for service injection
- [ ] All `@for` / `*ngFor` loops have `track` / `trackBy`
- [ ] No `any` types in component TypeScript
- [ ] SCSS uses BEM naming and CSS custom properties
- [ ] Spec file has at least 3 meaningful test cases
- [ ] All interactive elements have aria labels
