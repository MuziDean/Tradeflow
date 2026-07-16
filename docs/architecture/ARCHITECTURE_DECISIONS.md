# TradeFlow — Architecture Decision Records

## Index

- [ADR-001 — Modular Monolith Architecture](#adr-001--modular-monolith-architecture)
- [ADR-002 — Multi-Tenant by Tenant Isolation](#adr-002--multi-tenant-by-tenant-isolation)
- [ADR-003 — Host-Based Tenant Resolution](#adr-003--host-based-tenant-resolution)
- [ADR-004 — UUID Primary Keys](#adr-004--uuid-primary-keys)
- [ADR-005 — Clean Architecture + DDD](#adr-005--clean-architecture--ddd)
- [ADR-006 — Repository Pattern](#adr-006--repository-pattern)
- [ADR-007 — Service Layer Pattern](#adr-007--service-layer-pattern)
- [ADR-008 — Global Permissions](#adr-008--global-permissions)
- [ADR-009 — Tenant-Scoped Roles](#adr-009--tenant-scoped-roles)
- [ADR-010 — JWT Authentication](#adr-010--jwt-authentication)
- [ADR-011 — Redis Session Management](#adr-011--redis-session-management)
- [ADR-012 — Refresh Token Rotation](#adr-012--refresh-token-rotation)
- [ADR-013 — Role-Based Access Control](#adr-013--role-based-access-control)
- [ADR-014 — Branch-Scoped User Roles](#adr-014--branch-scoped-user-roles)
- [ADR-015 — Deny-by-Default Authorization](#adr-015--deny-by-default-authorization)
- [ADR-016 — Permission Cache Strategy](#adr-016--permission-cache-strategy)
- [ADR-017 — PostgreSQL + Redis + Celery Technology Stack](#adr-017--postgresql--redis--celery-technology-stack)
- [ADR-018 — Docker-based Development Environment](#adr-018--docker-based-development-environment)

---

## ADR-001 — Modular Monolith Architecture

**Status:** Accepted

**Context:**  
TradeFlow is an enterprise management platform requiring multiple bounded contexts: Identity & Access Management (IAM), Role-Based Access Control (RBAC), Platform/Company Management, Retail, Warehouse, Inventory, HR, Payroll, Audit, and Notifications. The team needs an architecture that balances development velocity with future scalability.

**Decision:**  
Adopt a **modular monolith** architecture. Each bounded context is implemented as a Django app under `apps/`. All modules share a single database, single deployment unit, and single codebase, but enforce strict boundaries through:
- Independent domain entities per module
- No cross-module imports (except shared infrastructure)
- Explicit API contracts via `apps/*/api/` layers
- Shared kernel in `core/` and `shared/`

**Alternatives Considered:**
1. **Microservices** — Rejected due to operational complexity, network latency, and distributed transaction challenges for a small team.
2. **Separate Django projects per module** — Rejected due to code duplication, deployment overhead, and tenant-join complexity.

**Consequences:**
- ✅ Fast development and deployment
- ✅ Strong module boundaries prevent accidental coupling
- ✅ Easy refactoring to microservices later if needed
- ✅ Single database simplifies cross-module queries
- ❌ Requires discipline to prevent god modules
- ❌ Deployment is all-or-nothing (mitigated by feature flags later)

**References:**
- [Software Architecture Document — Section 2: Architecture Style](https://www.notion.so/...)

---

## ADR-002 — Multi-Tenant by Tenant Isolation

**Status:** Accepted

**Context:**  
TradeFlow serves multiple independent companies (tenants). Each tenant’s data must be completely isolated. Options include separate databases per tenant, shared database with schema per tenant, or shared database with tenant_id discriminator.

**Decision:**  
Use **shared database, shared schema** with `tenant_id` discriminator on every data table. TenantMiddleware resolves `tenant_id` from the request host and sets `connection.tenant_id`. TenantModel base class auto-applies tenant filtering.

**Alternatives Considered:**
1. **Separate database per tenant** — Rejected due to cost, connection pooling limits, and operational complexity.
2. **Schema per tenant** — Rejected due to PostgreSQL schema migration complexity and connection limits.

**Consequences:**
- ✅ Cost-effective, simple operations
- ✅ Easy to add tenants
- ✅ Supports thousands of tenants on single DB
- ❌ Requires discipline to include `tenant_id` on every query
- ❌ Risk of data leak if tenant filtering is bypassed (mitigated by model base class)

**References:**
- [Database Design — Section 3: Multi-Tenant Strategy](https://www.notion.so/...)

---

## ADR-003 — Host-Based Tenant Resolution

**Status:** Accepted

**Context:**  
Each tenant must be identified from the incoming request. Options include subdomain, URL path prefix, or custom header.

**Decision:**  
Resolve tenant from **subdomain** (e.g., `tenant1.tradeflow.co.za`). Fallback to `X-Tenant-ID` header for API clients. TenantMiddleware extracts tenant and sets `request.actor.tenant_id`.

**Alternatives Considered:**
1. **URL path prefix** (`/api/v1/tenant1/...`) — Rejected due to verbosity and caching complexity.
2. **Custom header only** — Rejected due to poor UX for browser-based access.

**Consequences:**
- ✅ Clean URLs for web clients
- ✅ Natural fit for SaaS DNS
- ✅ Easy to test with `/etc/hosts`
- ❌ Requires wildcard DNS and SSL certificates
- ❌ Subdomain length limits (mitigated by short tenant slugs)

**References:**
- [Software Architecture — Section 4.1: API Gateway / Tenant Resolution](https://www.notion.so/...)

---

## ADR-004 — UUID Primary Keys

**Status:** Accepted

**Context:**  
Primary key strategy impacts migration compatibility, URL security, and merge replication.

**Decision:**  
Use **UUIDv4** as primary keys for all tables. UUIDs generated via `shared/ids/uuid.py` utility. Exposed in URLs and APIs.

**Alternatives Considered:**
1. **Auto-increment integers** — Rejected due to enumeration attacks and merge replication issues.
2. **ULID** — Considered but rejected in favor of standard UUID for simplicity.

**Consequences:**
- ✅ Unpredictable IDs (security through obscurity)
- ✅ Safe for distributed systems
- ✅ No merge conflicts
- ❌ Larger index size (16 bytes vs 4 bytes)
- ❌ Harder to read/debug manually

**References:**
- [Database Design — Section 4.2: Primary Keys](https://www.notion.so/...)

---

## ADR-005 — Clean Architecture + DDD

**Status:** Accepted

**Context:**  
Long-term maintainability requires clear separation of concerns and testability.

**Decision:**  
Implement **Clean Architecture** with Domain-Driven Design (DDD) principles:
- `domain/` — Entities, value objects, domain services (pure Python)
- `application/` — Use cases, orchestration (thin layer)
- `infrastructure/` — Persistence, external APIs, repositories
- `api/` — Serializers, views, URLs (thin adapters)
- `core/` — Cross-cutting concerns (auth, middleware, errors)

**Alternatives Considered:**
1. **Fat models / skinny views** — Rejected due to model bloat and testing difficulty.
2. **Service-only architecture** — Rejected due to anemic domain model.

**Consequences:**
- ✅ Highly testable (domain logic isolated)
- ✅ Framework-agnostic domain
- ✅ Clear ownership and boundaries
- ❌ More files and boilerplate
- ❌ Learning curve for new developers

**References:**
- [Backend Engineering Standards — Section 5: Architecture](https://www.notion.so/...)

---

## ADR-006 — Repository Pattern

**Status:** Accepted

**Context:**  
Direct ORM usage in views creates tight coupling and testing pain.

**Decision:**  
Use **Repository pattern** to abstract data access. Repositories live in `infrastructure/repositories.py` and expose domain methods (e.g., `get_by_email`, `save`). API views and services consume repositories, never the ORM directly.

**Alternatives Considered:**
1. **Direct Django ORM in views** — Rejected due to testability and coupling.
2. **Django Manager classes** — Rejected due to leaky abstraction and query complexity.

**Consequences:**
- ✅ Swappable data sources
- ✅ Testable with mocks
- ✅ Centralized query logic
- ❌ Boilerplate for simple CRUD

**References:**
- [Backend Engineering Standards — Section 5.2: Repository Pattern](https://www.notion.so/...)

---

## ADR-007 — Service Layer Pattern

**Status:** Accepted

**Context:**  
Business logic scattered across views and models leads to duplication and inconsistencies.

**Decision:**  
Use **Service layer** in `application/services.py` to orchestrate use cases. Services depend only on domain entities and repositories. Views are thin adapters that call services.

**Alternatives Considered:**
1. **Fat views** — Rejected due to duplication and poor testability.
2. **Model methods** — Rejected due to model bloat and persistence coupling.

**Consequences:**
- ✅ Reusable business logic
- ✅ Clear transaction boundaries
- ✅ Easy to test without HTTP layer
- ❌ Extra layer of indirection

**References:**
- [Backend Engineering Standards — Section 5.3: Service Layer](https://www.notion.so/...)

---

## ADR-008 — Global Permissions

**Status:** Accepted

**Context:**  
RBAC permissions should be consistent across tenants and centrally managed.

**Decision:**  
Permissions are **global system records** stored in `rbac_permissions` table without `tenant_id`. All tenants share the same permission catalog. Permissions are seeded via migrations and cannot be tenant-modified.

**Alternatives Considered:**
1. **Tenant-scoped permissions** — Rejected due to maintenance burden and inconsistency risk.
2. **Hybrid (core + custom)** — Added as future enhancement but not initial scope.

**Consequences:**
- ✅ Consistent permission names across tenants
- ✅ Easy to seed and maintain
- ✅ Enables wildcard matching across all tenants
- ❌ Tenants cannot create custom permissions (future workaround: namespacing)

**References:**
- [RBAC Design — Section 1: Permissions](https://www.notion.so/...)

---

## ADR-009 — Tenant-Scoped Roles

**Status:** Accepted

**Context:**  
Each tenant needs custom roles tailored to their organization.

**Decision:**  
Roles are **tenant-scoped** records in `rbac_roles` with `tenant_id`. Roles are unique per tenant (`unique_together: tenant_id, name`). System roles are pre-seeded but tenant-modifiable.

**Alternatives Considered:**
1. **Global roles** — Rejected because different tenants need different role structures.
2. **Role templates** — Considered for v2.

**Consequences:**
- ✅ Tenant autonomy
- ✅ Supports custom role names and descriptions
- ❌ Cannot share role definitions across tenants

**References:**
- [RBAC Design — Section 2: Roles](https://www.notion.so/...)

---

## ADR-010 — JWT Authentication

**Status:** Accepted

**Context:**  
TradeFlow needs stateless API authentication for mobile and SPA clients.

**Decision:**  
Use **JWT access tokens** (15-min TTL) with **opaque refresh tokens** stored server-side in Redis. Access JWT contains `sub`, `tid`, `sid`, `jti` claims. `TenantAwareJWTAuthentication` validates JWT `tid` against resolved tenant.

**Alternatives Considered:**
1. **Session cookies only** — Rejected due to mobile/native client limitations.
2. **Opaque tokens only** — Rejected due to introspect overhead.

**Consequences:**
- ✅ Stateless, scalable
- ✅ Works across mobile, web, API
- ✅ Tenant validation prevents cross-tenant reuse
- ❌ Revocation requires Redis store (refresh tokens)
- ❌ Access token leakage window is 15 min

**References:**
- [Auth Spec — Section 3: JWT Strategy](https://www.notion.so/...)
- [Security Architecture — Section 3.1-3.2](https://www.notion.so/...)

---

## ADR-011 — Redis Session Management

**Status:** Accepted

**Context:**  
Refresh tokens must be revocable and rotatable.

**Decision:**  
Store refresh tokens in **Redis** with session metadata. Each session has `session_id`, `refresh_token_hash`, `user_id`, `tenant_id`, `expires_at`, `revoked` flag. Rotation creates new session, revokes old.

**Alternatives Considered:**
1. **Database sessions** — Rejected due to DB load and no TTL support.
2. **JWT refresh tokens** — Rejected due to revocation complexity.

**Consequences:**
- ✅ Fast lookups
- ✅ TTL support
- ✅ Supports rotation and replay detection
- ❌ Redis dependency (acceptable — already required for cache)

**References:**
- [Security Architecture — Section 3.2: Session Store](https://www.notion.so/...)

---

## ADR-012 — Refresh Token Rotation

**Status:** Accepted

**Context:**  
Refresh tokens must not be reusable indefinitely.

**Decision:**  
Implement **refresh token rotation**: on each use, old token is revoked and a new token is issued. Replay detection revokes entire session family if token is reused after rotation.

**Alternatives Considered:**
1. **Static refresh tokens** — Rejected due to theft window.
2. **Short-lived refresh tokens (no rotation)** — Rejected due to poor UX.

**Consequences:**
- ✅ Limits theft window
- ✅ Replay detection alerts on attack
- ❌ Requires Redis session store

**References:**
- [Auth Spec — Section 3.2: Token Refresh](https://www.notion.so/...)
- [Security Architecture — Section 3.2](https://www.notion.so/...)

---

## ADR-013 — Role-Based Access Control

**Status:** Accepted

**Context:**  
Fine-grained authorization is required across all modules.

**Decision:**  
Implement **RBAC** with three entities: Permission (global), Role (tenant-scoped), UserRole (assignment with branch scope). Permissions use `resource.action` naming with wildcard support.

**Alternatives Considered:**
1. **ABAC only** — Too complex for initial implementation.
2. **ACL per user** — Doesn’t scale to 100+ permissions.

**Consequences:**
- ✅ Familiar model
- ✅ Scales to complex permissions via wildcards
- ✅ Future ABAC compatibility via service layer
- ❌ Role explosion risk (mitigated by wildcards and future ABAC layering)

**References:**
- [RBAC Design — Full Document](https://www.notion.so/...)

---

## ADR-014 — Branch-Scoped User Roles

**Status:** Accepted

**Context:**  
Multi-branch retailers need role assignments scoped to specific branches.

**Decision:**  
`UserRole` has nullable `branch_id`. Null = all branches. Specific `branch_id` restricts to that branch. Service layer enforces branch filtering automatically.

**Alternatives Considered:**
1. **Separate role per branch** — Too many roles.
2. **ABAC policies for branch** — Too complex for MVP.

**Consequences:**
- ✅ Matches real-world retail hierarchy
- ✅ Simple UI for role assignment
- ❌ Branch-aware queries required everywhere

**References:**
- [RBAC Design — Section 2.4: Branch Scoping](https://www.notion.so/...)

---

## ADR-015 — Deny-by-Default Authorization

**Status:** Accepted

**Context:**  
Authorization must prevent accidental exposure.

**Decision:**  
**Deny-by-default**: No resource is accessible unless an explicit permission is granted. No implicit allow lists.

**Alternatives Considered:**
1. **Allow-by-default with deny lists** — Rejected due to security risk.
2. **Opt-in per endpoint** — Rejected due to human forgetfulness.

**Consequences:**
- ✅ Secure by default
- ✅ Requires explicit permission assignment
- ❌ More permissions to manage

**References:**
- [Security Architecture — Section 4: Authorization](https://www.notion.so/...)

---

## ADR-016 — Permission Cache Strategy

**Status:** Accepted

**Context:**  
Permission evaluation on every request must be fast.

**Decision:**  
Cache user permissions in Redis using key format:  
`permissions:{tenant_id}:{user_id}:{permission_version}`  
TTL: 15 minutes. Invalidate by bumping `permission_version` on role change.

**Alternatives Considered:**
1. **No caching** — Too slow.
2. **Local memory cache** — Doesn’t work with multiple workers.
3. **Cache tags** — Over-engineered for MVP.

**Consequences:**
- ✅ Fast permission checks
- ✅ Automatic invalidation via version bump
- ❌ Permission updates have eventual consistency (15 min max)

**References:**
- [RBAC Design — Section 4: Caching Strategy](https://www.notion.so/...)

---

## ADR-017 — PostgreSQL + Redis + Celery Technology Stack

**Status:** Accepted

**Context:**  
Technology selection must support multi-tenancy, caching, async tasks, and enterprise scale.

**Decision:**  
- **Database:** PostgreSQL 14+ (JSON support, strong consistency)
- **Cache/Session:** Redis 7+ (TTL, pub/sub, high performance)
- **Task Queue:** Celery + Redis (async jobs, scheduling)
- **API:** Django REST Framework + SimpleJWT
- **Docs:** drf-spectacular (OpenAPI)

**Alternatives Considered:**
1. **MySQL** — Rejected due to inferior JSON and concurrency.
2. **RabbitMQ** — Considered but Redis already required.
3. **FastAPI** — Rejected due to Django ecosystem maturity for admin/auth.

**Consequences:**
- ✅ Battle-tested stack
- ✅ Excellent Django integration
- ✅ Supports enterprise features (notifications, reports)
- ❌ Celery operational complexity (mitigated by Docker Compose)

**References:**
- [Software Architecture — Section 7: Technology Stack](https://www.notion.so/...)

---

## ADR-018 — Docker-based Development Environment

**Status:** Accepted

**Context:**  
Developers need consistent, reproducible environments.

**Decision:**  
Provide **Docker Compose** setup for PostgreSQL, Redis, Celery, and Django. `docker-compose up` starts full stack. No local service installations required.

**Alternatives Considered:**
1. **Local installs per developer** — Rejected due to environment drift.
2. **Vagrant** — Rejected in favor of lighter-weight Docker.

**Consequences:**
- ✅ Consistent environments
- ✅ Easy onboarding
- ✅ Production-parity with Docker production
- ❌ Docker learning curve for new devs

**References:**
- [Software Architecture — Section 8: Deployment](https://www.notion.so/...)

---

## How to Use This Document

1. Each ADR is immutable once marked **Accepted**.
2. Create new ADRs for architectural decisions using the same template.
3. Reference ADRs in code comments and documentation.
4. Review ADRs quarterly for deprecation.