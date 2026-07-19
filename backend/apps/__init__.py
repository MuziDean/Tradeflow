"""
Business-domain modules for TradeFlow.

Each directory under apps/ is a bounded context module containing:
- api/: View layer (serializers, views, routes)
- domain/: Entities, value objects, domain services
- application/: Use cases (application services)
- infrastructure/: Module-specific external adapters

Per ADR-004: This package structure enables multiple teams to work
on different modules concurrently without step-on conflicts.
"""