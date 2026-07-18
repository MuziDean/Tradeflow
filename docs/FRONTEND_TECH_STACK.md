# TradeFlow — Frontend Technology Stack

**Date:** 2026-07-18
**Status:** Approved — Awaiting Implementation Approval

---

## Core

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 15.x | React framework with App Router, SSR/SSG |
| React | 19.x | UI library |
| TypeScript | 5.x | Type safety |

## UI & Styling

| Technology | Purpose |
|------------|---------|
| Tailwind CSS | Utility-first CSS framework |
| shadcn/ui | Component library (Radix UI + Tailwind) |
| Lucide React | Icon library |
| Framer Motion | Animation library |

## State & Data

| Technology | Purpose |
|------------|---------|
| TanStack Query | Server state, caching, synchronization |
| React Context | Authentication state, global settings |
| Zustand | Lightweight local state (optional) |

## Forms & Validation

| Technology | Purpose |
|------------|---------|
| React Hook Form | Form state management |
| Zod | Schema validation |

## HTTP & API

| Technology | Purpose |
|------------|---------|
| Axios | HTTP client |
| TanStack Table | Table/grid logic |
| Recharts | Charts |
| Sonner | Notifications |

## Utilities

| Technology | Purpose |
|------------|---------|
| clsx | Conditional class names |
| tailwind-merge | Tailwind class deduplication |
| date-fns | Date formatting |

## Code Quality

| Technology | Purpose |
|------------|---------|
| ESLint | Linting |
| Prettier | Formatting |
| Husky | Git hooks |
| lint-staged | Run linters on staged files |
| commitlint | Conventional commit enforcement |

## Testing

| Technology | Purpose |
|------------|---------|
| Vitest | Unit testing |
| React Testing Library | Component testing |
| Playwright | E2E testing (later) |

## Key Decisions

- **Next.js App Router** (not Pages Router) for layouts, Server Components, streaming
- **TanStack Query** as primary state manager (server state only)
- **shadcn/ui** for accessible, composable primitives
- **Zod** for runtime validation shared between client and inferred types

---

**Last Updated:** 2026-07-18