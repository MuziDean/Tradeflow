"""
Shared library package for TradeFlow.

Contains non-business-domain code shared across all modules:
ID generation, time utilities, domain event base classes,
outbox pattern primitives, storage abstraction, and encryption helpers.

Per Backend Engineering Standards: "shared services are platform utilities only,
not business logic."
"""