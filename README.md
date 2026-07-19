# TradeFlow

**Enterprise Retail, Warehouse, Inventory, HR & Payroll Management Platform**

A multi-tenant Django-based SaaS platform for South African retail businesses, built for scalability, security, and maintainability.

---

## Repository Structure

```
Tradeflow/
├── backend/                  # Django backend
│   ├── apps/                 # Bounded contexts (platform, iam, rbac, audit, retail, ...)
│   ├── config/               # Django project settings (base, development, staging, production, test)
│   ├── core/                 # Shared kernel (middleware, auth, permissions, errors, logging)
│   ├── shared/               # Domain utilities (ids, time, security, events, types, storage)
│   ├── infrastructure/       # Cross-cutting infrastructure (db, cache, queues, email, storage)
│   ├── tests/                # Global test suite (unit, contract, integration, performance, security)
│   ├── scripts/              # Dev/ops utility scripts
│   ├── docs/                 # Backend-specific documentation (arch, validation, runbooks)
│   ├── manage.py
│   ├── pyproject.toml
│   ├── .env.example
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── frontend/                 # Next.js frontend (planned)
│   ├── app/                  # App Router pages
│   ├── components/           # Shared UI (ui/, forms/, tables/, charts/, layout/, navigation/, feedback/)
│   ├── features/             # Feature modules (auth, company, branches, warehouses, users, roles, inventory, products, purchasing, sales, hr, reporting)
│   ├── hooks/                # Global custom hooks
│   ├── lib/                  # Third-party client configs (axios, query-client, permissions, utils)
│   ├── providers/            # React context providers
│   ├── services/             # API service layer
│   ├── types/                # TypeScript type definitions
│   ├── constants/            # App constants (API endpoints, permissions, routes)
│   ├── utils/                # Global utilities (cn, format, permissions, storage)
│   ├── styles/               # Global styles
│   ├── public/               # Static assets
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   └── README.md
│
├── docs/                     # Cross-cutting project docs (frontend planning, ADRs if shared)
├── docker/                   # Docker resources
├── .github/                  # CI/CD workflows
├── docker-compose.yml        # Root compose for full stack (backend + frontend + infra)
├── .gitignore
└── README.md
```

---

## Current Project Status

**Milestone 4 — Platform Management** ✅ Complete (production-ready)

| Milestone | Status | Completion |
|-----------|--------|------------|
| Phase 0 — Project Scaffold | ✅ Complete | 100% |
| Milestone 1 — Multi-Tenant Foundation | ✅ Complete | 100% |
| Milestone 2 — Authentication | ✅ Complete | 100% |
| Milestone 3 — RBAC | ✅ Complete | 100% |
| Milestone 4 — Platform Management | ✅ Complete | 100% |
| Milestone 5 — Product & Inventory Foundation | 📋 Planned | 0% |
| Frontend Architecture | 📋 Planned | 0% |

---

## Technology Stack

**Backend:**
- Python 3.11+ / Django 4.2+
- Django REST Framework
- SimpleJWT
- drf-spectacular (OpenAPI)
- PostgreSQL 14+
- Redis 7+
- Celery + Redis

**Frontend (planned):**
- Next.js 15 + React 19 + TypeScript
- Tailwind CSS + shadcn/ui
- TanStack Query + React Hook Form + Zod
- Axios + Recharts + Vitest

---

## Quick Start

### Backend

```bash
cd backend
cp .env.example .env
docker compose up --build
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Documentation

- **[Developer Guide](backend/docs/DEVELOPER_GUIDE.md)** — Coding standards, patterns, workflows
- **[Frontend Architecture Plan](docs/FRONTEND_ARCHITECTURE.md)** — Frontend design
- **[Milestone 5 Plan](docs/MILESTONE5_IMPLEMENTATION_PLAN.md)** — Product & Inventory roadmap

---

## License

Proprietary — TradeFlow Platform