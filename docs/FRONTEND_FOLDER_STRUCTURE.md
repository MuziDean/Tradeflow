# TradeFlow — Frontend Folder Structure

**Date:** 2026-07-18
**Status:** Approved — Awaiting Implementation Approval

---

## Root

```
frontend/
├── .github/                    # CI/CD workflows
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── .husky/                     # Git hooks
│   └── pre-commit
├── docs/                       # Frontend-specific documentation
│   ├── CONTRIBUTING.md
│   ├── DEPLOYMENT.md
│   └── COMPONENT_LIBRARY.md
├── docker/
│   └── Dockerfile
├── docker-compose.yml
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
├── .eslintrc.json
├── .prettierrc
├── commitlint.config.js
├── vitest.config.ts
├── playwright.config.ts
├── .env.local.example
├── .gitignore
└── README.md
```

---

## Source (`frontend/`)

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout (providers)
│   ├── page.tsx                # Landing page / redirect
│   ├── loading.tsx
│   ├── error.tsx
│   ├── not-found.tsx
│   ├── (auth)/                 # Unauthenticated routes
│   │   ├── layout.tsx          # Auth layout
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── forgot-password/
│   │   │   └── page.tsx
│   │   └── reset-password/
│   │       └── page.tsx
│   └── (dashboard)/            # Authenticated routes
│       ├── layout.tsx          # Dashboard shell (sidebar + header)
│       ├── page.tsx            # Dashboard home
│       ├── company/
│       │   └── page.tsx
│       ├── branches/
│       │   ├── page.tsx        # Branch list
│       │   └── [id]/
│       │       └── page.tsx    # Branch detail
│       ├── warehouses/
│       │   ├── page.tsx
│       │   └── [id]/
│       │       └── page.tsx
│       ├── users/
│       │   ├── page.tsx
│       │   └── [id]/
│       │       └── page.tsx
│       ├── roles/
│       │   ├── page.tsx
│       │   └── [id]/
│       │       └── page.tsx
│       ├── inventory/
│       │   ├── page.tsx
│       │   ├── products/
│       │   │   ├── page.tsx
│       │   │   └── [id]/
│       │   │       └── page.tsx
│       │   └── stock-movements/
│       │       └── page.tsx
│       ├── purchasing/
│       │   ├── page.tsx
│       │   └── purchase-orders/
│       │     └── [id]/
│       │         └── page.tsx
│       ├── sales/
│       │   ├── page.tsx
│       │   └── pos/
│       │     └── page.tsx
│       ├── hr/
│       │   ├── page.tsx
│       │   ├── employees/
│       │   │   └── page.tsx
│       │   └── attendance/
│       │     └── page.tsx
│       └── reporting/
│           ├── page.tsx
│           ├── sales-report/
│           │   └── page.tsx
│           └── inventory-report/
│               └── page.tsx
│
├── components/
│   ├── ui/                     # shadcn/ui primitives
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── table.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── toast.tsx
│   │   └── ...
│   ├── forms/                  # Reusable form components
│   │   ├── form-field.tsx
│   │   ├── form-input.tsx
│   │   ├── form-select.tsx
│   │   ├── form-textarea.tsx
│   │   └── form-error.tsx
│   ├── tables/                 # TanStack Table wrappers
│   │   ├── data-table.tsx
│   │   ├── table-pagination.tsx
│   │   └── table-toolbar.tsx
│   ├── charts/                 # Recharts wrappers
│   │   ├── bar-chart.tsx
│   │   ├── line-chart.tsx
│   │   ├── pie-chart.tsx
│   │   └── area-chart.tsx
│   ├── layout/                 # Layout primitives
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   ├── footer.tsx
│   │   ├── breadcrumbs.tsx
│   │   ├── page-header.tsx
│   │   └── container.tsx
│   ├── navigation/             # Navigation components
│   │   ├── main-nav.tsx
│   │   ├── user-menu.tsx
│   │   ├── tenant-switcher.tsx
│   │   └── sidebar-nav.tsx
│   └── feedback/               # Feedback components
│     ├── toast.tsx
│     ├── alert.tsx
│     ├── confirm-dialog.tsx
│     └── loading-spinner.tsx
│
├── features/                   # Feature modules
│   ├── auth/
│   │   ├── components/
│   │   │   ├── login-form.tsx
│   │   │   └── protected-route.tsx
│   │   ├── hooks/
│   │   │   ├── use-auth.ts
│   │   │   └── use-login.ts
│   │   ├── services/
│   │   │   └── auth.service.ts
│   │   ├── types/
│   │   │   └── auth.ts
│   │   ├── schemas/
│   │   │   └── auth.schema.ts
│   │   └── index.ts
│   ├── company/
│   │   ├── components/
│   │   │   ├── company-form.tsx
│   │   │   └── company-card.tsx
│   │   ├── hooks/
│   │   │   └── use-company.ts
│   │   ├── services/
│   │   │   └── company.service.ts
│   │   ├── types/
│   │   │   └── company.ts
│   │   ├── schemas/
│   │   │   └── company.schema.ts
│   │   └── index.ts
│   ├── branches/
│   │   ├── components/
│   │   │   ├── branch-form.tsx
│   │   │   ├── branch-table.tsx
│   │   │   └── branch-card.tsx
│   │   ├── hooks/
│   │   │   ├── use-branches.ts
│   │   │   └── use-create-branch.ts
│   │   ├── services/
│   │   │   └── branches.service.ts
│   │   ├── types/
│   │   │   └── branch.ts
│   │   ├── schemas/
│   │   │   └── branch.schema.ts
│   │   └── index.ts
│   ├── warehouses/
│   │   ├── components/
│   │   │   ├── warehouse-form.tsx
│   │   │   └── warehouse-select.tsx
│   │   ├── hooks/
│   │   │   └── use-warehouses.ts
│   │   ├── services/
│   │   │   └── warehouses.service.ts
│   │   ├── types/
│   │   │   └── warehouse.ts
│   │   ├── schemas/
│   │   │   └── warehouse.schema.ts
│   │   └── index.ts
│   ├── users/
│   │   ├── components/
│   │   │   ├── user-form.tsx
│   │   │   └── user-table.tsx
│   │   ├── hooks/
│   │   │   └── use-users.ts
│   │   ├── services/
│   │   │   └── users.service.ts
│   │   ├── types/
│   │   │   └── user.ts
│   │   ├── schemas/
│   │   │   └── user.schema.ts
│   │   └── index.ts
│   ├── roles/
│   │   ├── components/
│   │   │   ├── role-form.tsx
│   │   │   └── permission-tree.tsx
│   │   ├── hooks/
│   │   │   └── use-roles.ts
│   │   ├── services/
│   │   │   └── roles.service.ts
│   │   ├── types/
│   │   │   └── role.ts
│   │   ├── schemas/
│   │   │   └── role.schema.ts
│   │   └── index.ts
│   ├── inventory/
│   │   ├── components/
│   │   │   ├── stock-movement-form.tsx
│   │   │   └── stock-adjustment-form.tsx
│   │   ├── hooks/
│   │   │   ├── use-inventory.ts
│   │   │   └── use-stock-movements.ts
│   │   ├── services/
│   │   │   └── inventory.service.ts
│   │   ├── types/
│   │   │   └── inventory.ts
│   │   ├── schemas/
│   │   │   └── inventory.schema.ts
│   │   └── index.ts
│   ├── products/
│   │   ├── components/
│   │   │   ├── product-form.tsx
│   │   │   ├── product-card.tsx
│   │   │   └── product-table.tsx
│   │   ├── hooks/
│   │   │   ├── use-products.ts
│   │   │   └── use-create-product.ts
│   │   ├── services/
│   │   │   └── products.service.ts
│   │   ├── types/
│   │   │   ├── product.ts
│   │   │   └── variant.ts
│   │   ├── schemas/
│   │   │   └── product.schema.ts
│   │   └── index.ts
│   ├── purchasing/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   ├── schemas/
│   │   └── index.ts
│   ├── sales/
│   │   ├── components/
│   │   │   ├── pos-terminal.tsx
│   │   │   └── cart.tsx
│   │   ├── hooks/
│   │   │   └── use-pos.ts
│   │   ├── services/
│   │   │   └── sales.service.ts
│   │   ├── types/
│   │   │   └── sale.ts
│   │   ├── schemas/
│   │   │   └── sale.schema.ts
│   │   └── index.ts
│   ├── hr/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   ├── schemas/
│   │   └── index.ts
│   └── reporting/
│       ├── components/
│       │   ├── report-filters.tsx
│       │   ├── sales-chart.tsx
│       │   └── export-buttons.tsx
│       ├── hooks/
│       │   └── use-reports.ts
│       ├── services/
│       │   └── reports.service.ts
│       ├── types/
│       │   └── report.ts
│       ├── schemas/
│       │   └── report.schema.ts
│       └── index.ts
│
├── hooks/                      # Global custom hooks
│   ├── use-auth.ts
│   ├── use-tenant.ts
│   ├── use-permissions.ts
│   ├── use-media-query.ts
│   └── use-debounce.ts
│
├── lib/                        # Third-party configurations
│   ├── axios.ts                # Axios instance + interceptors
│   ├── query-client.ts         # TanStack Query client
│   ├── permissions.ts          # Permission utilities
│   └── utils.ts                # General utilities
│
├── services/                   # Global API clients
│   ├── api.ts                  # Base API class
│   ├── auth.service.ts
│   ├── company.service.ts
│   ├── branches.service.ts
│   ├── warehouses.service.ts
│   ├── users.service.ts
│   ├── roles.service.ts
│   ├── inventory.service.ts
│   ├── products.service.ts
│   ├── purchasing.service.ts
│   ├── sales.service.ts
│   ├── hr.service.ts
│   └── reporting.service.ts
│
├── types/                      # Global TypeScript types
│   ├── auth.ts
│   ├── company.ts
│   ├── branch.ts
│   ├── warehouse.ts
│   ├── user.ts
│   ├── role.ts
│   ├── product.ts
│   ├── inventory.ts
│   ├── sale.ts
│   ├── report.ts
│   ├── api.ts                  # API response envelope types
│   └── index.ts
│
├── providers/                  # React context providers
│   ├── auth-provider.tsx
│   ├── query-provider.tsx
│   ├── theme-provider.tsx
│   └── toast-provider.tsx
│
├── constants/                  # App constants
│   ├── api-endpoints.ts
│   ├── permissions.ts
│   ├── routes.ts
│   └── app-config.ts
│
├── styles/                     # Global styles
│   └── globals.css
│
├── utils/                      # Global utilities
│   ├── cn.ts                   # clsx + tailwind-merge
│   ├── format.ts               # Date/number formatting
│   ├── permissions.ts          # Permission checking helpers
│   └── storage.ts              # LocalStorage utilities
│
├── public/                     # Static assets
│   ├── favicon.ico
│   ├── logo.svg
│   └── images/
│
├── middleware.ts               # Next.js middleware (auth guard)
└── .env.local.example
```

---

## Folder Responsibilities

### `app/`
Next.js App Router routes. Only route-level code. Calls feature hooks/components.

### `components/`
- **ui/**: shadcn/ui primitives. No business logic.
- **forms/**: Form field wrappers.
- **tables/**: Data table implementations.
- **charts/**: Chart wrappers around Recharts.
- **layout/**: Shell components (header, sidebar).
- **navigation/**: Nav menus, breadcrumbs.
- **feedback/**: Toasts, alerts, confirm dialogs.

### `features/`
Isolated business capability modules. Each feature owns its UI, logic, and data access.

### `hooks/`
Global reusable hooks (auth, media queries, debounce).

### `lib/`
Third-party client configuration. Single responsibility per file.

### `services/`
API service layer. Each service maps to a backend module.

### `types/`
TypeScript type definitions. Shared across features.

### `providers/`
React Context providers wrapping the app.

### `constants/`
Static configuration strings (API endpoints, permissions, routes).

### `utils/`
Pure utility functions.

### `public/`
Static assets.

---

**Last Updated:** 2026-07-18