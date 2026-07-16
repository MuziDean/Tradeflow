# TradeFlow

**Enterprise Retail, Warehouse, Inventory, HR & Payroll Management Platform**

A multi-tenant Django-based SaaS platform for South African retail businesses, built for scalability, security, and maintainability.

---

## Current Project Status

**Milestone 1:** ✅ Multi-Tenant Foundation — Complete  
**Milestone 2:** ✅ Authentication — Complete  
**Milestone 3:** ✅ RBAC (Role-Based Access Control) — Complete  

---

## Completed Milestones

### Milestone 0 — Project Scaffold
- Django project structure with modular apps
- Core middleware (tenant, request ID, logging)
- Health check endpoints
- Standardized error envelope and pagination

### Milestone 1 — Multi-Tenant Foundation
- `TenantMiddleware` — Subdomain-based tenant resolution
- `TenantModel` base class — Auto tenant filtering
- Shared schema, shared database architecture
- PostgreSQL + Redis + Celery infrastructure

### Milestone 2 — Authentication
- Register, login, logout, token refresh
- JWT access tokens with opaque refresh tokens
- Rate limiting, lockout, security events
- Password reset flow
- `TenantAwareJWTAuthentication`

### Milestone 3 — RBAC
- Global permissions with wildcard support
- Tenant-scoped roles
- Branch-scoped user roles
- Permission cache with version invalidation
- DRF permission classes (`HasPermission`, `HasBranchAccess`)

---

## Technology Stack

**Backend:**
- Python 3.11+ / Django 4.2+
- Django REST Framework
- SimpleJWT
- drf-spectacular (OpenAPI)

**Data:**
- PostgreSQL 14+
- Redis 7+
- Celery + Redis

**Infrastructure:**
- Docker + Docker Compose
- Nginx (production)
- Gunicorn (production)

**Testing:**
- pytest / Django TestCase
- Factory Boy (planned)

---

## Folder Structure

```
tradeflow-backend/
├── config/                    # Django project settings
│   ├── settings/              # Environment-specific settings
│   ├── urls.py                # Root URL config
│   ├── wsgi.py                # WSGI app
│   └── asgi.py                # ASGI app
├── core/                      # Shared kernel
│   ├── middleware/            # Tenant, request ID, logging
│   ├── auth/                  # JWT authentication
│   ├── permissions/           # Base permission classes
│   ├── errors/                # Error envelope
│   ├── pagination.py          # Standard pagination
│   └── logging/               # Logging config
├── shared/                    # Domain utilities
│   ├── ids/                   # UUID generators
│   ├── time/                  # Timezone helpers
│   ├── security/              # Encryption utilities
│   └── types/                 # Enums
├── infrastructure/            # Cross-cutting infrastructure
│   ├── db/                    # Base models
│   ├── cache/                 # Redis client
│   ├── queues/                # Celery config
│   ├── email/                 # Email sender
│   └── storage/               # Object storage
├── apps/                      # Bounded contexts
│   ├── platform/              # Company/branch management
│   ├── iam/                   # Authentication & users
│   ├── rbac/                  # Roles & permissions
│   ├── audit/                 # Audit log
│   ├── retail/                # Retail module scaffold
│   └── [other modules]/       # HR, Inventory, etc.
├── docs/                      # Documentation
│   ├── architecture/          # ADRs
│   ├── DEVELOPER_GUIDE.md
│   └── PROJECT_STATUS.md
├── tests/                     # Global tests
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml / requirements.txt
```

---

## Development Workflow

### Prerequisites
- Docker Desktop
- Python 3.11+ (for local IDE support)
- Node.js (for frontend, separate repo)

### Environment Setup

```bash
# Clone repository
git clone https://github.com/MuziDean/Tradeflow.git
cd tradeflow-backend

# Copy environment file
cp .env.example .env

# Edit .env with your settings
# - SECRET_KEY
# - DATABASE_URL
# - REDIS_URL
# - ALLOWED_HOSTS
```

### Development Commands

```bash
# Start full stack (PostgreSQL, Redis, Django, Celery)
docker compose up --build

# Run tests
docker compose exec web python manage.py test

# Create migrations
docker compose exec web python manage.py makemigrations

# Apply migrations
docker compose exec web python manage.py migrate

# Django shell
docker compose exec web python manage.py shell

# Celery worker logs
docker compose logs -f celery
```

---

## How to Start the Project

### Using Docker (Recommended)

```bash
docker compose up --build
```

Django server will be available at `http://localhost:8000`.

### Local Development (Without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Run PostgreSQL and Redis locally
# Update DATABASE_URL and REDIS_URL in .env

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Run Celery worker (separate terminal)
celery -A config worker -l info
```

---

## How to Run Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test apps.iam

# Specific test class
python manage.py test apps.iam.tests.test_authentication_service

# With coverage
pip install coverage
python manage.py test --verbosity=2
```

---

## Architecture Overview

TradeFlow follows **Clean Architecture + DDD** principles in a **modular monolith** structure.

### Key Principles

1. **Multi-Tenancy:** Shared database, shared schema, `tenant_id` discriminator
2. **Security:** Deny-by-default RBAC, JWT + refresh tokens, rate limiting, audit events
3. **Scalability:** Redis caching, Celery async tasks, permission versioning
4. **Maintainability:** Strict module boundaries, repository pattern, service layer

### Layer Responsibilities

- **Domain** (`domain/`): Entities, value objects, domain logic
- **Application** (`application/`): Use cases, orchestration
- **Infrastructure** (`infrastructure/`): ORM, repositories, external integrations
- **API** (`api/`): Serializers, views, URLs
- **Core** (`core/`): Cross-cutting concerns

### Request Flow

1. `TenantMiddleware` resolves tenant from host
2. `TenantAwareJWTAuthentication` validates JWT and checks tenant
3. Middleware loads user permissions into `request.actor`
4. DRF permission class checks authorization
5. View calls service layer
6. Service uses repositories
7. Repository manages ORM

---

## API Documentation

When running locally with DEBUG=True:
- Swagger UI: `http://localhost:8000/api/v1/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/v1/schema/redoc/`
- OpenAPI JSON: `http://localhost:8000/api/v1/schema/`

---

## Documentation

- **[Architecture Decisions](docs/architecture/ARCHITECTURE_DECISIONS.md)** — ADR catalog
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** — Coding standards, patterns, workflows
- **[Project Status](docs/PROJECT_STATUS.md)** — Live project status and metrics

---

## Contributing

Please refer to [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) before contributing.

### Git Workflow

1. Create feature branch from `main`
2. Implement with tests
3. Push and create PR
4. Ensure CI passes
5. Squash-merge to main

---

## License

Proprietary — TradeFlow Platform

---

**Last Updated:** 2026-07-16