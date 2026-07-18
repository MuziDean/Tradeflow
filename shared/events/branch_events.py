"""
Branch domain events.

Emitted by BranchService on state changes.
"""

from shared.events.base import DomainEvent


class BranchCreated(DomainEvent):
    def __init__(self, tenant_id: str, branch_id: str, name: str):
        super().__init__(
            "branch.created",
            {"tenant_id": tenant_id, "branch_id": branch_id, "name": name},
        )