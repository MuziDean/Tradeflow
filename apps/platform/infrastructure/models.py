"""
Django models for the platform module.

Per Database Design Section 4.1 (platform): tenant + tenant_domain + subscription.
Per Security Architecture §5.2: Defense-in-depth tenant isolation.

The Tenant model is the root identity — it does NOT inherit from TenantModel
because the Tenant itself is the owner, not tenant-scoped data.
CompanyProfile and other platform entities ARE tenant-scoped via TenantModel.
"""

from uuid import uuid4

from django.db import models

from infrastructure.db.base_model import TenantModel


class Tenant(models.Model):
    """
    Master tenant (company) record.

    This is the root identity for all tenant isolation.
    tenant_id = id (one-to-one). Not tenant-scoped by TenantModel
    because the Tenant IS the tenant boundary.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(
        max_length=20,
        default="active",
        choices=[
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("trial", "Trial"),
            ("cancelled", "Cancelled"),
        ],
    )
    subscription_plan = models.CharField(max_length=50, default="basic")
    settings = models.JSONField(default=dict, blank=True)
    branding = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "platform_tenants"
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def __str__(self) -> str:
        return f"Tenant({self.slug})"


class TenantDomain(models.Model):
    """
    Domain/subdomain mapping for tenant routing.

    Per Database Design §4.1: supports subdomain and custom-domain SaaS routing.
    TenantMiddleware resolves tenant from request host using this table.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="domains"
    )
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "platform_tenant_domains"
        verbose_name = "Tenant Domain"
        verbose_name_plural = "Tenant Domains"
        indexes = [
            models.Index(fields=["domain", "tenant"]),
        ]

    def __str__(self) -> str:
        return f"{self.domain} → {self.tenant.slug}"


class CompanyProfile(TenantModel):
    """
    Extended company profile for a tenant.

    Tenant-scoped via TenantModel base. Linked 1:1 to a Tenant.
    """

    legal_name = models.CharField(max_length=255, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    address = models.JSONField(default=dict, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    logo_url = models.URLField(blank=True)

    class Meta:
        db_table = "platform_company_profiles"
        verbose_name = "Company Profile"
        verbose_name_plural = "Company Profiles"
        unique_together = ("tenant_id",)