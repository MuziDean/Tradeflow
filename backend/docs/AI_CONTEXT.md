# TradeFlow AI Context

This document is the canonical onboarding guide for future AI assistants working on TradeFlow. It must be treated as the current source of truth for architecture, implementation standards, and project status.

---

## 1. Project Overview and Vision

TradeFlow is a modular monolith SaaS platform for retail, warehouse, inventory, HR, and payroll operations in South Africa. The platform is built for multi-tenant enterprise use and is designed to evolve from a single deployment into a more distributed system later without rewriting its domain model.

The long-term goal is to provide a complete operational backbone for modern retail and distribution businesses, including:
- tenant-aware company and branch management
- identity and access control
- product and inventory management
- purchasing, sales, warehouse operations, and reporting

---

## 2. Current Implementation Status

Current status as of 2026-07-19:
- Phase 0 complete
- Milestone 1 complete
- Milestone 2 complete
- Milestone 3 complete
- Milestone 4 complete
- Milestone 5 Step 1 complete (inventory domain foundation)

The inventory module now contains:
- domain entities for products, suppliers, pricing, stock, transfers, reservations, and stock takes
- Django ORM models with tenant-aware inheritance and index/constraint structure
- repository implementations for persistence-only operations

Services, APIs, serializers, and business logic remain out of scope for this step.

---

## 3. Folder Responsibilities

- backend/apps/: bounded contexts such as platform, iam, rbac, inventory
- backend/config/: Django project wiring and environment configuration
- backend/core/: shared cross-cutting concerns such as auth, middleware, permissions, errors, and pagination
- backend/shared/: reusable domain utilities and enums
- backend/infrastructure/: cross-cutting infrastructure wrappers such as the tenant base model and storage/cache abstractions
- backend/docs/: architecture, status, and milestone documentation

---

## 4. Complete Backend Architecture

The backend follows a modular monolith architecture:
- each bounded context lives in its own Django app under backend/apps/
- each module uses Clean Architecture + DDD boundaries
- shared infrastructure is centralized in backend/core, backend/shared, and backend/infrastructure
- the system uses a shared database and shared schema with tenant isolation via tenant_id

The primary architectural layers are:
- domain/: pure Python entities and value objects
- application/: use case orchestration and service layer
- infrastructure/: ORM models, repositories, persistence adapters
- api/: serializers, views, urls

---

## 5. Clean Architecture and DDD Rules

These rules are mandatory:
- business logic belongs only inside application services
- domain entities contain business rules only
- infrastructure contains persistence only
- API views remain thin
- serializers only validate and serialize
- repository classes never contain business logic
- domain events are emitted only from services

Do not introduce framework dependencies into the domain layer.

---

## 6. Repository Pattern Conventions

Repositories are persistence abstractions for aggregates.
They must:
- live in infrastructure/repositories.py
- expose domain-oriented methods such as get_by_id, list_for_tenant, create, update, soft_delete
- return domain entities, not ORM models
- never embed business rules

---

## 7. Service Layer Conventions

Services belong in application/services.py and should:
- orchestrate use cases
- coordinate domain entities and repositories
- manage transactions and domain events
- remain free of HTTP/DRF dependencies

Services are not part of Step 1 and should not be implemented unless explicitly requested.

---

## 8. API Layer Conventions

The API layer is thin and adapter-oriented:
- serializers validate and serialize
- views handle request/response translation
- URLs are module-local and versioned under the API root
- RBAC permission checks are enforced on protected endpoints

---

## 9. Domain Event Conventions

Domain events are part of the service layer and are emitted only when application services perform a state transition.
Event names should be explicit, such as:
- ProductCreated
- ProductUpdated
- InventoryAdjusted

The domain layer should not emit events directly in Step 1-style scaffolding.

---

## 10. Tenant Isolation Strategy

Tenant isolation is mandatory.
Every tenant-scoped model must inherit from the shared TenantModel base and use tenant_id as the discriminator.
Rules:
- tenant_id must never be accepted from user input
- tenant context is resolved from the request and injected by middleware
- all writes should use transaction.atomic() in service-level code
- every query should remain tenant-scoped by design

---

## 11. Authentication Architecture

Authentication is implemented through JWT and DRF integration.
The backend uses:
- access tokens and refresh tokens
- tenant-aware JWT authentication
- opaque refresh token patterns
- rate limiting and lockout handling

The authentication module is the responsibility of the IAM bounded context.

---

## 12. RBAC Architecture

RBAC is implemented as a separate bounded context and is enforced through permission classes.
Key rules:
- permissions are global in the catalog and shared across tenants
- tenant-scoped roles are assigned to users within a tenant
- protected endpoints must enforce permissions explicitly
- deny-by-default authorization is the standard

---

## 13. Platform Module Overview

The Platform module is the reference implementation for future modules. It demonstrates:
- domain entities
- ORM models
- repositories
- tenant-aware conventions
- soft-delete patterns
- audit-friendly field structure

New modules should follow Platform closely.

---

## 14. Coding Standards

- follow PEP 8 and Black formatting
- use type hints
- use docstrings on public classes and methods
- use logging rather than print()
- keep imports explicit and sorted
- maintain consistency with existing modules

---

## 15. Naming Conventions

- files and modules use snake_case
- classes use PascalCase
- methods and variables use snake_case
- repositories end with Repository
- services end with Service
- serializers end with Serializer
- views end with View

Database names should use snake_case and be prefixed by the app name where appropriate.

---

## 16. Error Handling Conventions

- use custom exception classes from core errors where appropriate
- do not swallow exceptions silently
- log exceptions with logger.exception()
- return standardized API error envelopes

---

## 17. Logging Conventions

- use module-level loggers
- prefer structured logging in production
- include tenant_id, request_id, and user_id where relevant
- do not use print() for runtime diagnostics

---

## 18. Security Rules

- never trust client-supplied tenant identifiers
- enforce RBAC on every protected endpoint
- enforce tenant isolation on all data access
- use UUID primary keys
- keep secrets in environment configuration
- never place business logic in views or serializers

---

## 19. Database Conventions

- use PostgreSQL
- use UUID primary keys for all entities
- use tenant_id on every tenant-scoped model
- use DecimalField for money values
- include created_at and updated_at on relevant models
- add indexes and unique constraints where appropriate
- use soft delete only where appropriate

---

## 20. Frontend Architecture

The frontend is planned as a separate Next.js application with feature-based modules. It will consume the backend through REST APIs and be tenant-aware via the authenticated session.

The frontend stack is expected to include:
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- React Hook Form + Zod

---

## 21. Technology Stack

Backend:
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Docker Compose

Frontend (planned):
- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui

---

## 22. Development Workflow

1. review relevant docs before changing architecture
2. inspect existing modules before implementing new ones
3. keep changes scoped to the requested milestone step
4. verify changes with Django checks or relevant tests
5. update the status and AI documentation after meaningful changes

---

## 23. Git Workflow

- work in feature branches
- keep commits focused and descriptive
- update documentation alongside implementation changes
- avoid mixing milestone steps in a single commit where possible

---

## 24. Current Milestone

Milestone 5 — Inventory & Product Management
- Step 1 complete: domain entities, ORM models, repositories
- Step 2+ pending approval before implementation

---

## 25. Remaining Roadmap

Remaining work:
- Step 2: products, variants, images, and barcodes
- Step 3: prices, costs, supplier integration, and inventory flows
- later milestones for services, APIs, validation, and frontend integration

---

## 26. Important Architectural Decisions (Summary of ADRs)

Key ADRs:
- modular monolith architecture
- shared database with tenant_id isolation
- UUID primary keys
- Clean Architecture + DDD
- repository pattern
- service layer pattern
- RBAC with deny-by-default authorization

---

## 27. Rules That Must Never Be Broken

- do not place business logic in views, serializers, or repositories
- do not bypass tenant isolation
- do not implement services or APIs unless the current step explicitly requires them
- do not create cross-module imports that violate the module boundaries
- do not skip documentation updates after major architectural changes

---

## 28. Checklist for Any AI Before Writing New Code

- read the relevant documentation first
- inspect the reference module (Platform first)
- confirm whether the task is domain, infrastructure, application, or API work
- keep the change aligned with the repository pattern
- ensure tenant isolation and RBAC requirements are preserved
- update status and AI documentation after the change

---

## 29. Maintenance Note

Any future architectural decision or milestone change must be reflected in both AI_CONTEXT.md and PROJECT_STATUS.md so the repository remains consistent and self-documenting.
