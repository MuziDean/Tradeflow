# TradeFlow — Developer Guide

This guide ensures every future module follows the same architecture and coding standards.

---

## Table of Contents

1. [Coding Standards](#coding-standards)
2. [Naming Conventions](#naming-conventions)
3. [Folder Responsibilities](#folder-responsibilities)
4. [Layer Responsibilities](#layer-responsibilities)
5. [Repository Pattern](#repository-pattern)
6. [Service Pattern](#service-pattern)
7. [Testing Strategy](#testing-strategy)
8. [Git Workflow](#git-workflow)
9. [Branch Naming Convention](#branch-naming-convention)
10. [Pull Request Checklist](#pull-request-checklist)
11. [How New Modules Should Be Built](#how-new-modules-should-be-built)

---

## Coding Standards

### Python Style

- Follow **PEP 8** strictly
- Use **Black** formatter (line length 120)
- Use **isort** for import sorting
- Use **flake8** for linting
- Maximum line length: 120 characters

### Type Hints

- All function signatures must have type hints
- Use `list[str]`, `dict[str, int]` instead of `List[str]`, `Dict[str, int]` (Python 3.9+)
- Use `X | None` instead of `Optional[X]` (Python 3.10+)
- Use `X | Y` instead of `Union[X, Y]` (Python 3.10+)

### Docstrings

- All public classes, methods, and functions must have docstrings
- Use Google-style docstrings:

```python
def function_name(param: str) -> bool:
    """
    Short description.

    Longer description if needed.

    Args:
        param: Description of param.

    Returns:
        Description of return value.
    """
```

### Error Handling

- Use custom exception classes from `core.errors`
- Never catch generic `Exception` without re-raising
- Always log exceptions with `logger.exception()`
- Return standardized error envelopes via `core.errors.envelope`

### Logging

- Use module-level logger: `logger = logging.getLogger("tradeflow.module_name")`
- Use structured logging (JSON in production)
- Never use `print()` — always use logger

---

## Naming Conventions

### Files

- **Domain entities:** `domain/entities.py`
- **Repositories:** `infrastructure/repositories.py`
- **Services:** `application/services.py`
- **Serializers:** `api/serializers.py`
- **Views:** `api/views.py`
- **URLs:** `api/urls.py`
- **Tests:** `tests/test_<module>.py`

### Classes

- **Entities:** PascalCase (e.g., `UserAccount`, `Permission`)
- **Repositories:** PascalCase + `Repository` suffix (e.g., `UserRepository`)
- **Services:** PascalCase + `Service` suffix (e.g., `AuthenticationService`)
- **Serializers:** PascalCase + `Serializer` suffix (e.g., `UserSerializer`)
- **Views:** PascalCase + `View` suffix (e.g., `UserListView`)

### Functions/Methods

- **snake_case** (e.g., `get_by_email`, `create_user`)
- Boolean getters use `is_` or `has_` prefix (e.g., `is_locked`, `has_permission`)

### Variables

- **snake_case** (e.g., `user_id`, `tenant_id`)
- Private variables use underscore prefix (e.g., `_cache_key`)

### Constants

- **UPPER_SNAKE_CASE** (e.g., `MAX_FAILED_ATTEMPTS`, `DEFAULT_PAGE_SIZE`)

### Database Tables

- Prefix with app name: `iam_user_accounts`, `rbac_roles`, `platform_companies`
- Use snake_case for field names

---

## Folder Responsibilities

### `config/`

Django project configuration. Contains:
- `settings/` — Environment-specific settings (base, development, staging, production, test)
- `urls.py` — Root URL configuration
- `wsgi.py` / `asgi.py` — WSGI/ASGI entry points

**Rule:** No business logic here. Only configuration.

### `core/`

Shared kernel used by all apps. Contains:
- `middleware/` — Tenant, request ID, logging middleware
- `auth/` — JWT authentication classes
- `permissions/` — Base DRF permission classes
- `errors/` — Error envelope, exception handler
- `pagination.py` — Standard pagination
- `logging/` — Logging configuration

**Rule:** Framework-agnostic where possible. No app-specific logic.

### `shared/`

Domain utilities shared across apps. Contains:
- `ids/` — UUID generators
- `time/` — Timezone helpers
- `security/` — Encryption utilities
- `events/` — Event bus base classes
- `storage/` — Object storage abstractions
- `types/` — Enums and type definitions

**Rule:** Pure Python, no Django imports if possible.

### `infrastructure/`

Cross-cutting infrastructure. Contains:
- `db/` — Base models (TenantModel)
- `cache/` — Redis client wrapper
- `queues/` — Celery configuration
- `email/` — Email sender abstraction
- `storage/` — S3/minio client

**Rule:** Thin wrappers around third-party libraries.

### `apps/`

Bounded contexts. Each app follows Clean Architecture:
```
apps/<module>/
├── domain/
│   └── entities.py          # Domain entities
├── application/
│   └── services.py          # Use case orchestration
├── infrastructure/
│   ├── models.py            # Django ORM models
│   ├── repositories.py      # Repository implementations
│   └── [external].py        # External API clients
├── api/
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # DRF views
│   └── urls.py              # URL routing
└── tests/
    ├── __init__.py
    ├── test_<module>.py     # Unit tests
    └── test_<module>_api.py # API tests
```

**Rule:** Strict boundaries. No cross-app imports except `shared/` and `infrastructure/`.

---

## Layer Responsibilities

### Domain Layer (`domain/`)

- **Pure Python** — no framework dependencies
- Contains: Entities, value objects, domain services, domain events
- Business rules and invariants
- Must be testable without Django/DRF

**Example:**
```python
from dataclasses import dataclass
from shared.ids.uuid import new_id_str
from shared.time.helpers import now

@dataclass
class UserAccount:
    id: str = field(default_factory=new_id_str)
    email: str = ""
    failed_login_attempts: int = 0

    def is_locked(self) -> bool:
        return self.failed_login_attempts >= MAX_FAILED_ATTEMPTS
```

### Application Layer (`application/`)

- **Thin orchestration layer**
- Depends only on domain entities and repositories
- No framework imports (no DRF, no Django ORM)
- Contains: Use cases, application services, DTOs

**Example:**
```python
class AuthenticationService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate(self, email: str, password: str) -> UserAccount | None:
        user = self.user_repository.get_by_email(email)
        if user and user.check_password(password):
            return user
        return None
```

### Infrastructure Layer (`infrastructure/`)

- **Implementation details**
- Contains: ORM models, repository implementations, external API clients
- Depends on Django, third-party libraries

**Example:**
```python
class UserRepository:
    def get_by_email(self, email: str) -> UserAccount | None:
        try:
            model = UserAccountModel.objects.get(email=email)
            return self._to_entity(model)
        except UserAccountModel.DoesNotExist:
            return None
```

### API Layer (`api/`)

- **Thin adapters**
- Contains: Serializers, views, URLs
- No business logic — only request/response mapping
- Calls application services

**Example:**
```python
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AuthenticationService(user_repository=UserRepository())
        user = service.authenticate(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        return Response({"user": UserSerializer(user).data})
```

---

## Repository Pattern

### Definition

Repository abstracts data access. Views and services depend on repository interfaces, not ORM directly.

### Rules

1. **Repository methods return domain entities, not ORM models**
2. **Repository methods accept domain entities as parameters**
3. **One repository per aggregate root**
4. **Repositories are thin — no business logic**
5. **Use `_to_entity()` and `_from_entity()` for conversion**

### Example

```python
# infrastructure/repositories.py
class UserRepository:
    def get_by_email(self, tenant_id: str, email: str) -> UserAccount | None:
        try:
            model = UserAccountModel.objects.get(tenant_id=tenant_id, email=email)
            return self._to_entity(model)
        except UserAccountModel.DoesNotExist:
            return None

    def save(self, user: UserAccount) -> UserAccount:
        model = UserAccountModel(**user.to_dict())
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: UserAccountModel) -> UserAccount:
        return UserAccount(
            id=str(model.id),
            email=model.email,
            # ...
        )
```

### Anti-Patterns

- ❌ ORM queries in views
- ❌ ORM queries in services
- ❌ Business logic in repositories
- ❌ Returning ORM models from repositories

---

## Service Pattern

### Definition

Service layer orchestrates use cases. It depends only on domain entities and repositories.

### Rules

1. **Services are thin — orchestrate, don’t implement business logic in entities**
2. **Services accept repositories via constructor (dependency injection)**
3. **One service per use case or bounded context**
4. **Services return domain entities or DTOs, never ORM models**
5. **Services can call other services**

### Example

```python
# application/services.py
class AuthenticationService:
    def __init__(self, user_repository: UserRepository, security_event_repository: SecurityEventRepository):
        self.user_repository = user_repository
        self.security_event_repository = security_event_repository

    def authenticate(self, tenant_id: str, email: str, password: str) -> UserAccount | None:
        user = self.user_repository.get_by_email(tenant_id, email)
        if user and user.check_password(password):
            self.user_repository.reset_failed_attempts(user)
            self.security_event_repository.log("LOGIN_SUCCEEDED", user_id=user.id)
            return user
        return None
```

### Anti-Patterns

- ❌ Business logic in views
- ❌ Direct ORM access in services
- ❌ Services returning HTTP responses
- ❌ God services that do everything

---

## Testing Strategy

### Test Types

1. **Unit Tests** — `tests/test_<module>.py`
   - Test domain entities
   - Test services with mocked repositories
   - Fast, no database

2. **Integration Tests** — `tests/test_<module>_integration.py`
   - Test repositories with test database
   - Test service + repository together
   - Use Django `TestCase`

3. **API Tests** — `tests/test_<module>_api.py`
   - Test endpoints with DRF test client
   - Test authentication, permissions, serialization
   - Use `APITestCase`

4. **Cross-Tenant Security Tests** — `tests/test_cross_tenant.py`
   - Verify tenant isolation
   - Verify no cross-tenant data leaks
   - Verify permission isolation

### Test Naming

```python
class TestClassName(TestCase):
    def test_method_should_do_something(self):
        """Docstring describing test."""
        pass
```

### Test Coverage

- Aim for 80%+ coverage
- All security-critical paths must be tested
- All permission checks must be tested
- All cross-tenant boundaries must be tested

### Example Unit Test

```python
def test_authenticate_success(self):
    """Test successful authentication resets failed attempts."""
    user = UserAccount(tenant_id="1", email="test@example.com")
    user.set_password("password")
    self.user_repo.get_by_email.return_value = user

    result = self.service.authenticate("1", "test@example.com", "password")

    self.assertIsNotNone(result)
    self.user_repo.reset_failed_attempts.assert_called_once_with(user)
```

---

## Git Workflow

### Branching Strategy

- `main` — Production-ready code
- `feature/*` — New features
- `fix/*` — Bug fixes
- `refactor/*` — Code refactoring
- `docs/*` — Documentation only

### Workflow

1. Create branch from `main`
2. Implement feature with tests
3. Run tests locally
4. Commit with conventional commit message
5. Push and create PR
6. Address review feedback
7. Squash-merge to `main`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add user registration endpoint
fix: resolve token refresh race condition
refactor: extract permission matching logic
docs: update README with Docker commands
test: add cross-tenant security tests
```

Format: `<type>(<scope>): <description>`

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`

---

## Branch Naming Convention

```
<type>/<ticket-id>-<short-description>

Examples:
feature/AUTH-101-add-login-endpoint
fix/RBAC-205-role-permission-cache-bug
refactor/IAM-300-extract-password-service
docs/PLATFORM-400-update-api-docs
```

---

## Pull Request Checklist

Before creating a PR:

- [ ] All tests pass (`python manage.py test`)
- [ ] New code has tests (unit + integration)
- [ ] No linting errors (`flake8`)
- [ ] Code formatted with `black`
- [ ] Imports sorted with `isort`
- [ ] Docstrings added for public methods
- [ ] Type hints complete
- [ ] No console.log or print statements
- [ ] Security review completed (auth, tenant isolation, permissions)
- [ ] Documentation updated (if applicable)
- [ ] ADR created (if architectural change)

### PR Description Template

```markdown
## Summary
Brief description of changes.

## Motivation
Why is this change needed?

## Changes
- List of changes made

## Test Plan
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing completed

## Security Considerations
- [ ] Tenant isolation verified
- [ ] Authorization tested
- [ ] No sensitive data exposed
```

---

## How New Modules Should Be Built

### Step 1: Create Module Structure

```bash
mkdir -p apps/<module>/domain
mkdir -p apps/<module>/application
mkdir -p apps/<module>/infrastructure
mkdir -p apps/<module>/api
mkdir -p apps/<module>/tests
touch apps/<module>/__init__.py
touch apps/<module>/domain/__init__.py
touch apps/<module>/application/__init__.py
touch apps/<module>/infrastructure/__init__.py
touch apps/<module>/api/__init__.py
touch apps/<module>/tests/__init__.py
```

### Step 2: Define Domain Entities

Create `apps/<module>/domain/entities.py`:
- Define entities using `@dataclass`
- Add business logic methods
- No framework dependencies

### Step 3: Create Django Models

Create `apps/<module>/infrastructure/models.py`:
- Inherit from `TenantModel` if tenant-scoped
- Define database schema
- Add Meta class with db_table, indexes, constraints

### Step 4: Create Repositories

Create `apps/<module>/infrastructure/repositories.py`:
- One repository per aggregate root
- Methods return domain entities
- Use `_to_entity()` for ORM → domain conversion

### Step 5: Create Services

Create `apps/<module>/application/services.py`:
- One service per use case
- Depend on repositories (constructor injection)
- Orchestrate business logic

### Step 6: Create API Layer

Create:
- `apps/<module>/api/serializers.py`
- `apps/<module>/api/views.py`
- `apps/<module>/api/urls.py`

Views must be thin — call services only.

### Step 7: Wire URLs

Update `config/api_urls.py`:
```python
path("api/v1/<module>/", include("apps.<module>.api.urls")),
```

### Step 8: Add to INSTALLED_APPS

Update `config/settings/base.py`:
```python
PLATFORM_APPS = [
    # ...
    "apps.<module>",
]
```

### Step 9: Write Tests

Create:
- `apps/<module>/tests/test_<module>.py` — Unit tests
- `apps/<module>/tests/test_<module>_api.py` — API tests

### Step 10: Create Migrations

```bash
python manage.py makemigrations <module>
python manage.py migrate
```

### Checklist for New Module

- [ ] Domain entities defined
- [ ] Django models created with correct indexes
- [ ] Repositories implemented
- [ ] Services implemented
- [ ] API layer (serializers, views, URLs)
- [ ] URLs wired in `config/api_urls.py`
- [ ] App added to `INSTALLED_APPS`
- [ ] Unit tests written
- [ ] API tests written
- [ ] Migrations created
- [ ] Tenant isolation verified
- [ ] Permission checks added
- [ ] Security events emitted
- [ ] Documentation updated

---

## Module Communication Rules

### Allowed

- `apps/<module>/api/` → `apps/<module>/application/`
- `apps/<module>/application/` → `apps/<module>/domain/`
- `apps/<module>/infrastructure/` → `apps/<module>/domain/`
- Any module → `core/`
- Any module → `shared/`

### Forbidden

- `apps/<module>/domain/` → any other layer
- `apps/<module>/application/` → `infrastructure/`
- `apps/<module>/api/` → `infrastructure/`
- Cross-app imports (except `shared/` and `infrastructure/`)

---

## Security Best Practices

1. **Always filter by `tenant_id`** — Never query without tenant filter
2. **Deny-by-default** — Always check permissions
3. **Never trust user input** — Validate and sanitize
4. **Hash passwords** — Use `make_password` / `check_password`
5. **Hash tokens** — Never store plaintext tokens
6. **Rate limit auth endpoints** — Prevent brute force
7. **Log security events** — Login, logout, permission changes
8. **Use HttpOnly cookies** — For refresh tokens
9. **Validate JWT `tid` claim** — Prevent cross-tenant reuse
10. **Escape SQL** — Use parameterized queries only

---

## Performance Best Practices

1. **Use `select_related()` / `prefetch_related()`** — Avoid N+1 queries
2. **Cache permissions** — Use Redis with version invalidation
3. **Use database indexes** — On all foreign keys and filter fields
4. **Paginate responses** — Use `StandardPagination`
5. **Use async tasks** — For email, reports, heavy operations
6. **Monitor query count** — Use Django Debug Toolbar in development

---

## Common Pitfalls

1. **Forgetting tenant filter** — Always include `tenant_id` in queries
2. **Business logic in views** — Move to service layer
3. **ORM models in API responses** — Convert to domain entities
4. **Missing docstrings** — Add them before merging
5. **Skipping tests** — Write tests for all security-critical paths
6. **Hardcoding URLs** — Use `reverse()` or named URLs
7. **Ignoring CORS** — Configure properly for frontend
8. **Storing plaintext secrets** — Use environment variables

---

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)

---

**Last Updated:** 2026-07-16