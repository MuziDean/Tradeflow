# TradeFlow — Frontend Architecture

**Date:** 2026-07-18
**Status:** Planning Complete — Awaiting Implementation Approval

---

## 1. Purpose

The TradeFlow frontend is a **separate repository** (`tradeflow-frontend`) that consumes the TradeFlow backend API. It is a **tenant-aware SaaS frontend** for South African retail businesses.

This document defines the frontend architecture, technology stack, folder structure, backend integration contract, and implementation plan for Milestone 5.

---

## 2. Architecture Principles

### 2.1 Separation of Concerns

- **Backend** (`tradeflow-backend`): Django + DRF, Clean Architecture + DDD
- **Frontend** (`tradeflow-frontend`): Next.js + React, feature-based architecture
- **Communication**: REST API via Axios, JWT authentication, standard JSON envelope

### 2.2 Feature-Based Organization

The frontend is organized by **business capability** (feature modules), not by technical layer. Each feature is self-contained:

```
features/
├── auth/           # Authentication & authorization
├── company/        # Company profile, preferences
├── branches/       # Branch management
├── warehouses/     # Warehouse management
├── users/          # User management
├── roles/          # Role & permission management
├── inventory/      # Inventory & products
├── purchasing/     # Purchase orders
├── sales/          # POS, sales transactions
├── hr/             # Employees, attendance, leave
├── reporting/      # Reports & analytics
```

### 2.3 Shared Infrastructure

Common UI components, hooks, utilities, and services are shared across features:

```
components/ui/      # Reusable UI primitives (shadcn/ui)
hooks/              # Custom React hooks
lib/                # Third-party client configs (Axios, TanStack Query)
services/           # API service clients
types/              # TypeScript type definitions
```

### 2.4 Tenant Awareness

Every API request includes the tenant context derived from the JWT `tid` claim. The Axios interceptor automatically attaches the tenant context. The frontend never explicitly handles tenant resolution — it is implicit in the authenticated session.

---

## 3. Technology Stack

### 3.1 Core

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 15 | React framework, App Router, SSR/SSG |
| React | 19 | UI library |
| TypeScript | 5.x | Type safety |

### 3.2 UI & Styling

| Technology | Purpose |
|------------|---------|
| Tailwind CSS | Utility-first CSS |
| shadcn/ui | Component library (Radix UI + Tailwind) |
| Lucide React | Icons |
| Framer Motion | Animations |

### 3.3 State & Data

| Technology | Purpose |
|------------|---------|
| TanStack Query | Server state, caching, synchronization |
| React Context | Authentication state, global settings |
| Zustand | Lightweight local state (if needed) |

### 3.4 Forms & Validation

| Technology | Purpose |
|------------|---------|
| React Hook Form | Form state management |
| Zod | Schema validation |

### 3.5 HTTP & API

| Technology | Purpose |
|------------|---------|
| Axios | HTTP client |
| TanStack Table | Table/grid logic |
| Recharts | Charts & graphs |
| Sonner | Notifications |

### 3.6 Utilities

| Technology | Purpose |
|------------|---------|
| clsx | Conditional class names |
| tailwind-merge | Tailwind class deduplication |
| date-fns | Date formatting |

### 3.7 Quality

| Technology | Purpose |
|------------|---------|
| ESLint | Linting |
| Prettier | Formatting |
| Husky | Git hooks |
| lint-staged | Run linters on staged files |
| Vitest | Unit testing |
| React Testing Library | Component testing |
| Playwright | E2E testing (later) |

---

## 4. Application Structure

```
tradeflow-frontend/
├── .github/                    # CI/CD workflows
├── .husky/                     # Git hooks
├── docs/                       # Frontend-specific documentation
├── frontend/                   # Source code (... this is the actual app)
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/             # Auth routes (login, forgot-password)
│   │   ├── (dashboard)/        # Authenticated dashboard routes
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/                 # shadcn/ui primitives
│   │   ├── forms/              # Reusable form components
│   │   ├── tables/             # Data tables with TanStack Table
│   │   ├── charts/             # Recharts wrappers
│   │   ├── layout/             # Header, sidebar, footer, breadcrumbs
│   │   ├── navigation/         # Nav menus, sidebars
│   │   └── feedback/           # Toasts, alerts, confirm dialogs
│   ├── features/               # Feature modules
│   │   ├── auth/
│   │   ├── company/
│   │   ├── branches/
│   │   ├── warehouses/
│   │   ├── users/
│   │   ├── roles/
│   │   ├── inventory/
│   │   ├── products/
│   │   ├── purchasing/
│   │   ├── sales/
│   │   ├── hr/
│   │   └── reporting/
│   ├── hooks/
│   │   ├── use-auth.ts
│   │   ├── use-tenant.ts
│   │   ├── use-permissions.ts
│   │   └── ...
│   ├── lib/
│   │   ├── axios.ts            # Axios instance with interceptors
│   │   ├── query-client.ts     # TanStack Query client
│   │   └── utils.ts
│   ├── services/               # API clients
│   │   ├── auth.service.ts
│   │   ├── company.service.ts
│   │   ├── branches.service.ts
│   │   └── ...
│   ├── types/
│   │   ├── auth.ts
│   │   ├── company.ts
│   │   ├── api.ts
│   │   └── index.ts
│   ├── providers/
│   │   ├── auth-provider.tsx
│   │   ├── query-provider.tsx
│   │   └── theme-provider.tsx
│   ├── constants/
│   │   ├── api-endpoints.ts
│   │   ├── permissions.ts
│   │   └── routes.ts
│   ├── styles/
│   │   └── globals.css
│   ├── utils/
│   │   ├── cn.ts
│   │   ├── format.ts
│   │   └── permissions.ts
│   ├── public/
│   ├── middleware.ts           # Next.js middleware (auth guard)
│   └── .env.local.example
├── docker/
│   └── Dockerfile
├── docker-compose.yml
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
├── .eslintrc.json
├── .prettierrc
└── README.md
```

---

## 5. Feature Module Contract

Each feature module follows this internal structure:

```
features/<feature>/
├── components/          # Feature-specific UI components
├── hooks/               # Feature-specific hooks
├── services/            # API service wrapper
├── types/               # TypeScript types
├── schemas/             # Zod validation schemas
├── utils/               # Feature utilities
└── index.ts             # Public exports
```

### 5.1 Public API of a Feature

A feature exposes:

- **Components**: Reusable UI for this domain
- **Hooks**: Stateful logic (`use-branches.ts`, `use-create-branch.ts`)
- **Services**: API methods (`branches.service.ts`)
- **Types**: Domain types (`Branch`, `BranchCreateInput`)
- **Schemas**: Validation schemas (`branchSchema`)

Other features should **not** import from internal paths of another feature.

---

## 6. Next.js App Router Layout

```
app/
├── (auth)/                    # Unauthenticated routes
│   ├── login/
│   ├── forgot-password/
│   └── layout.tsx             # Auth layout (no nav sidebar)
├── (dashboard)/               # Authenticated routes
│   ├── company/
│   ├── branches/
│   ├── warehouses/
│   ├── users/
│   ├── roles/
│   ├── inventory/
│   ├── products/
│   ├── purchasing/
│   ├── sales/
│   ├── hr/
│   ├── reporting/
│   ├── layout.tsx             # Dashboard shell (sidebar + header)
│   └── page.tsx               # Dashboard home
├── layout.tsx                 # Root layout (providers)
└── page.tsx                   # Landing / redirect
```

Route groups `(auth)` and `(dashboard)` share the same URL namespace while using different layouts. The root `layout.tsx` wraps with providers (`QueryProvider`, `AuthProvider`, `ThemeProvider`).

---

## 7. State Management Strategy

### 7.1 Server State — TanStack Query

All API data lives in TanStack Query. This is the **primary state management** solution.

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['branches', tenantId],
  queryFn: () => branchesService.list(tenantId),
});
```

### 7.2 Client State — React Context + Zustand

- **Auth context**: Current user, tenant, permissions, tokens
- **Zustand (optional)**: UI preferences, lightweight global state

---

## 8. Design System

### 8.1 shadcn/ui

Base component library built on Radix UI primitives. Components live in `components/ui/` and are customized via Tailwind.

### 8.2 Tailwind Theme

```ts
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: 'hsl(...)',
        // brand colors
      }
    }
  }
}
```

### 8.3 Responsive

Mobile-first. Breakpoints:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

---

## 9. Code Quality Standards

### 9.1 Linting

- ESLint with Next.js recommended config
- Custom rules for Accessibility, React hooks, TypeScript

### 9.2 Formatting

- Prettier with default settings
- Tailwind plugin for class sorting

### 9.3 Git Hooks

- `pre-commit`: lint-staged runs `eslint --fix` and `prettier --write`
- `commit-msg`: commitlint for conventional commits

### 9.4 Testing

- Vitest for unit tests
- React Testing Library for component tests
- Playwright for E2E (later)

---

## 10. Deployment

### 10.1 Development

```bash
npm run dev          # Next.js dev server at localhost:3000
```

### 10.2 Production

- **Vercel** (preferred) or **self-hosted Docker**
- Build: `npm run build`
- Start: `npm run start`
- Environment variables via `.env.local`

### 10.3 Environment Configuration

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

**Last Updated:** 2026-07-18