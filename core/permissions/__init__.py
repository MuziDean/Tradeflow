"""
Permission base classes for TradeFlow.

Provides base permission classes that enforce tenant context,
branch scoping, and RBAC evaluation. Used as base classes for
all DRF view permissions.

Per documentation Section 7.3-7.5: Permission classes must evaluate
tenant context, branch scope, and log privileged denials.
"""