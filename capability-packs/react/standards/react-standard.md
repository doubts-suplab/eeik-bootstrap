# React Engineering Standard

Version: React 18/19 | Next.js 14+ | TypeScript 5.x | TanStack Query v5

---

## Golden Rules

| # | Rule | Enforcement |
|---|------|-------------|
| R01 | Functional components only — no class components | Code review |
| R02 | `"strict": true` in tsconfig — no `any` | CI lint |
| R03 | Server Components by default in Next.js App Router | Architecture review |
| R04 | `use client` explicitly declared — never inferred | Code review |
| R05 | Custom hooks for all stateful logic extraction | Code review |
| R06 | Stable keys in lists — never array index | Code review |
| R07 | Error boundaries on all async subtrees | Code review |
| R08 | No `console.log` in production | post-edit hook |
| R09 | Zod schema for all external data (API responses, forms) | Code review |
| R10 | TanStack Query for all server state — no manual `useEffect` fetch | Code review |

---

## Server vs Client Component Decision

```
Is there user interaction? (onClick, onChange, useState, useEffect)
  YES → 'use client'
  NO  → Server Component (default)

Does it need browser APIs? (window, localStorage, IntersectionObserver)
  YES → 'use client'
  NO  → Server Component

Does it subscribe to real-time data?
  YES → 'use client' + WebSocket/SSE
  NO  → Server Component with revalidate
```

**Rule**: Push `use client` as far down the tree as possible.

---

## Data Fetching Strategy

| Scenario | Tool | Pattern |
|----------|------|---------|
| Static page data | Next.js fetch (Server Component) | `fetch(url, { next: { revalidate: 3600 } })` |
| Dynamic server data | Server Component async/await | Direct DB/API call |
| Client-side data | TanStack Query | `useQuery` |
| Mutations | TanStack Query + Server Actions | `useMutation` + `revalidatePath` |
| Real-time | SWR with polling or WebSocket | `{ refreshInterval: 5000 }` |

Never use `useEffect` for data fetching — use TanStack Query or Server Components.

---

## State Management

```
URL state (filters, pagination, search)        → next/navigation searchParams
Server state (API data)                         → TanStack Query
Local component state (UI, toggles)             → useState / useReducer
Shared UI state (modal open, selected item)     → Zustand
Global auth/session                             → next-auth + server session
Form state                                      → React Hook Form + Zod
```

---

## TypeScript Conventions

```typescript
// Props — use interface
interface ButtonProps {
  label: string;
  variant?: 'primary' | 'secondary';
  onClick: () => void;
  children?: React.ReactNode;
}

// API response — use Zod schema and infer type
const UserSchema = z.object({ id: z.string(), name: z.string(), email: z.string().email() });
type User = z.infer<typeof UserSchema>;

// Avoid:
type AnyProps = { [key: string]: any };     // ❌
const handleClick = (e: any) => {};        // ❌
```

---

## Performance

- `React.memo` only after profiling — not preemptively
- `useCallback` / `useMemo` only for expensive computations or stable references passed to memo'd children
- Dynamic imports: `const Chart = dynamic(() => import('./Chart'), { ssr: false })`
- Image: always use `next/image` — never `<img>` in Next.js
- Font: `next/font` — never `<link>` for Google Fonts

---

## Security

- **Server Actions** validate input with Zod before any DB operation
- **Never trust** `searchParams` or `params` — parse and validate
- **CSRF**: Next.js Server Actions include CSRF protection automatically
- **`dangerouslySetInnerHTML`**: never use without sanitization (DOMPurify)
- **env vars**: `NEXT_PUBLIC_` prefix only for client-safe values
