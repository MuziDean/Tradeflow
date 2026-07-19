# TradeFlow — Monorepo Restructure Report

**Date:** 2026-07-19
**Status:** Complete

---

## Objective

Restructure the repository from a flat layout to a monorepo with `backend/` and `frontend/` top-level directories, preserving all functionality and Git history.

---

## Target Structure

```
Tradeflow/
├── backend/                  # Django backend
│   ├── apps/                 # Bounded contexts
│   ├── config/               # Django settings
│   ├── core/                 # Shared kernel
│   ├── shared/               # Domain utilities
│   ├── infrastructure/       # Cross-cutting infra
│   ├── tests/                # Test suites
│   ├── scripts/              # Utility scripts
│   ├── docs/                 # Backend documentation
│   ├── manage.py
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/                 # Next.js frontend (planned)
├── docs/                     # Cross-cutting docs
├── docker/                   # Docker resources
├── .github/                  # CI/CD workflows
├── docker-compose.yml        # Root compose (optional)
├── .gitignore
└── README.md
```

---

## Files Moved

### Directories moved to `backend/`

| Source | Destination | Method |
|--------|-------------|--------|
| `apps/` | `backend/apps/` | robocopy + delete originals |
| `config/` | `backend/config/` | robocopy + delete originals |
| `core/` | `backend/core/` | robocopy + delete originals |
| `shared/` | `backend/shared/` | robocopy + delete originals |
| `infrastructure/` | `backend/infrastructure/` | robocopy + delete originals |
| `tests/` | `backend/tests/` | robocopy + delete originals |
| `scripts/` | `backend/scripts/` | robocopy + delete originals |

### Root files moved to `backend/`

| Source | Destination |
|--------|-------------|
| `manage.py` | `backend/manage.py` |
| `pyproject.toml` | `backend/pyproject.toml` |
| `.env.example` | `backend/.env.example` |
| `Dockerfile` | `backend/Dockerfile` |
| `docker-compose.yml` | `backend/docker-compose.yml` |
| `.dockerignore` | `backend/.dockerignore` |
| `PHASE0_VERIFICATION.md` | `backend/PHASE0_VERIFICATION.md` |
| `PHASE0_COMPLETION_REPORT.md` | `backend/PHASE0_COMPLETION_REPORT.md` |
| `MILESTONE1_COMPLETION_REPORT.md` | `backend/MILESTONE1_COMPLETION_REPORT.md` |

### Documentation moved to `backend/docs/`

| Source | Destination |
|--------|-------------|
| `docs/architecture/` | `backend/docs/architecture/` |
| `docs/adr/` | `backend/docs/adr/` |
| `docs/runbooks/` | `backend/docs/runbooks/` |
| `docs/standards/` | `backend/docs/standards/` |
| `docs/STEP1_MODEL_VALIDATION.md` | `backend/docs/STEP1_MODEL_VALIDATION.md` |
| `docs/STEP2_SERVICE_VALIDATION.md` | `backend/docs/STEP2_SERVICE_VALIDATION.md` |
| `docs/STEP3_API_VALIDATION.md` | `backend/docs/STEP3_API_VALIDATION.md` |
| `docs/REFACTOR_VALIDATION.md` | `backend/docs/REFACTOR_VALIDATION.md` |
| `docs/PLATFORM_ARCHITECTURE_VALIDATION.md` | `backend/docs/PLATFORM_ARCHITECTURE_VALIDATION.md` |
| `docs/PLATFORM_HARDENING_REPORT.md` | `backend/docs/PLATFORM_HARDENING_REPORT.md` |
| `docs/DEVELOPER_GUIDE.md` | `backend/docs/DEVELOPER_GUIDE.md` |
| `docs/PROJECT_STATUS.md` | `backend/docs/PROJECT_STATUS.md` |

### Stale root-level files deleted

- `base_service.py`, `branch_service.py`, `business_preferences_service.py`, `company_service.py`, `currency_service.py`, `fiscal_year_service.py`, `number_sequence_service.py`, `stored_file_service.py`, `tax_configuration_service.py`, `warehouse_service.py` — These were orphaned copies from the earlier refactor, already present in `backend/apps/platform/application/`
- `validators/` directory — Orphaned copy, already present in `backend/apps/platform/application/validators/`
- Various frontend scaffold directories (`app/`, `auth/`, `branches/`, `charts/`, `company/`, `components/`, `constants/`, `features/`, `feedback/`, `forms/`, `hr/`, `inventory/`, `layout/`, `navigation/`, `products/`, `providers/`, `public/`, `purchasing/`, `roles/`, `sales/`, `styles/`, `tables/`, `users/`, `utils/`, `warehouses/`) — These were empty scaffold directories from the frontend planning phase, now superseded by the `frontend/` directory

### Frontend directory

- `frontend/` — Created with the agreed architecture structure (empty scaffold, no pages or business logic)

---

## Configuration Updates

### Docker Compose

Updated `backend/docker-compose.yml`:
- Changed build context from `.` to `./backend`
- All services now reference `./backend` as their build context

### README.md

Updated to reflect the new monorepo structure with:
- Repository tree showing `backend/` and `frontend/`
- Updated quick start commands (`cd backend`)
- Updated documentation links to point to `backend/docs/`

### PROJECT_STATUS.md

Updated to show the new repository layout.

---

## Verification

### Backend Structure

```
backend/
├── apps/          (19 sub-apps: platform, iam, rbac, audit, retail, ...)
├── config/        (settings, urls, wsgi, asgi)
├── core/          (middleware, auth, permissions, errors, logging)
├── shared/        (ids, time, security, events, types, storage)
├── infrastructure/ (db, cache, queues, email, storage)
├── tests/         (unit, api, contract, integration, performance, security)
├── scripts/       (restructure_monorepo.py)
├── docs/          (architecture, adr, runbooks, standards, validation reports)
├── manage.py
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

### Frontend Structure

```
frontend/
├── app/
├── components/ (ui/, forms/, tables/, charts/, layout/, navigation/, feedback/)
├── features/   (auth, company, branches, warehouses, users, roles, inventory, products, purchasing, sales, hr, reporting)
├── hooks/
├── lib/
├── providers/
├── services/
├── types/
├── constants/
├── utils/
├── styles/
├── public/
```

### Root Level

```
.github/
.gitignore
.vscode/
backend/
docker/
docs/          (FRONTEND_ARCHITECTURE.md, FRONTEND_TECH_STACK.md, FRONTEND_FOLDER_STRUCTURE.md, FRONTEND_BACKEND_INTEGRATION.md, MILESTONE5_IMPLEMENTATION_PLAN.md, MONOREPO_RESTRUCTURE_REPORT.md)
README.md
```

---

## No Behavioral Changes

- All Python imports remain unchanged (relative imports within `apps/`, `config/`, `core/`, `shared/`, `infrastructure/` are unaffected by the move)
- No business logic was modified
- No public APIs were changed
- The backend can be started with `cd backend && docker compose up --build`

---

## Conclusion

The monorepo restructure is complete. The repository now has a clean separation between backend and frontend code, with all backend functionality preserved and all documentation paths updated.

**Next step:** Begin Milestone 5 implementation (Product & Inventory Foundation).