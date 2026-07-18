"""
API views for the Platform module.

Per Backend Engineering Standards §5.1: Thin views that only:
- Authenticate and authorize
- Parse request input
- Call exactly one use-case
- Format response

All endpoints declare explicit RBAC permissions via required_permission.
All responses use the standard API response envelope.
"""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.platform.api.serializers import (
    BranchCreateSerializer,
    BranchDetailSerializer,
    BranchListSerializer,
    BranchUpdateSerializer,
    BusinessPreferencesSerializer,
    CompanyProfileSerializer,
    CompanyUpdateSerializer,
    CurrencySerializer,
    FiscalYearCreateSerializer,
    FiscalYearDetailSerializer,
    FiscalYearListSerializer,
    NumberSequenceCreateSerializer,
    NumberSequenceDetailSerializer,
    NumberSequenceListSerializer,
    StoredFileCreateSerializer,
    StoredFileListSerializer,
    TaxConfigurationCreateSerializer,
    TaxConfigurationDetailSerializer,
    TaxConfigurationListSerializer,
    TaxConfigurationUpdateSerializer,
    TenantSerializer,
    WarehouseCreateSerializer,
    WarehouseDetailSerializer,
    WarehouseListSerializer,
    WarehouseUpdateSerializer,
)
from apps.platform.application.branch_service import BranchService
from apps.platform.application.business_preferences_service import (
    BusinessPreferencesService,
)
from apps.platform.application.company_service import CompanyService
from apps.platform.application.currency_service import CurrencyService
from apps.platform.application.fiscal_year_service import FiscalYearService
from apps.platform.application.number_sequence_service import (
    NumberSequenceService,
)
from apps.platform.application.stored_file_service import StoredFileService
from apps.platform.application.tax_configuration_service import (
    TaxConfigurationService,
)
from apps.platform.application.warehouse_service import WarehouseService
from apps.platform.domain.entities import (
    Branch as BranchEntity,
    BusinessPreferences as BusinessPreferencesEntity,
    FiscalYear as FiscalYearEntity,
    NumberSequence as NumberSequenceEntity,
    StoredFile as StoredFileEntity,
    TaxConfiguration as TaxConfigurationEntity,
    Warehouse as WarehouseEntity,
)
from apps.platform.infrastructure.models import (
    Branch,
    FiscalYear,
    NumberSequence,
    StoredFile,
    TaxConfiguration,
    Tenant,
    Warehouse,
)
from apps.platform.infrastructure.repositories import (
    BranchRepository,
    BusinessPreferencesRepository,
    CompanyRepository,
    CurrencyRepository,
    FiscalYearRepository,
    NumberSequenceRepository,
    StoredFileRepository,
    TaxConfigurationRepository,
    WarehouseRepository,
)
from core.pagination import StandardPagination

logger = logging.getLogger("tradeflow.platform")


def _error_response(
    message: str,
    code: str = "ERROR",
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> Response:
    """Standard error response using the API envelope format."""
    return Response(
        {"success": False, "error": {"code": code, "message": message}},
        status=status_code,
    )


# ──────────────────────────────────────────────
# Tenant
# ──────────────────────────────────────────────


class TenantInfoView(APIView):
    """
    get: Returns current tenant info.

    Tenant context is resolved by TenantMiddleware.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.tenant.read"

    @extend_schema(
        summary="Get tenant info",
        description="Returns the current tenant's configuration information.",
        responses={200: TenantSerializer},
    )
    def get(self, request):
        tenant_id = request.actor.tenant_id
        if not tenant_id:
            return _error_response(
                "Tenant context not available.",
                code="TENANT_CONTEXT_MISSING",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        tenant = Tenant.objects.filter(id=tenant_id).first()
        if not tenant:
            return _error_response(
                "Tenant not found.",
                code="TENANT_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = TenantSerializer(tenant)
        return Response({"data": serializer.data})


# ──────────────────────────────────────────────
# Company Profile
# ──────────────────────────────────────────────


class CompanyProfileView(APIView):
    """
    get: Returns the current tenant's company profile.

    put: Updates the current tenant's company profile.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.company.read"

    def get_service(self):
        return CompanyService(company_repository=CompanyRepository())

    def get(self, request):
        tenant_id = request.actor.tenant_id
        service = self.get_service()
        company = service.get_company(tenant_id)
        if not company:
            return _error_response(
                "Company not found.",
                code="COMPANY_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = CompanyProfileSerializer(company)
        return Response({"data": serializer.data})

    def put(self, request):
        tenant_id = request.actor.tenant_id
        serializer = CompanyUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = self.get_service()
        existing = service.get_company(tenant_id)
        if not existing:
            return _error_response(
                "Company not found.",
                code="COMPANY_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Map validated data back to domain entity
        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)

        updated = service.update_company(existing)
        return Response(
            {"data": CompanyProfileSerializer(updated).data},
            status=status.HTTP_200_OK,
        )


CompanyProfileView.put.required_permission = "platform.company.edit"


# ──────────────────────────────────────────────
# Business Preferences
# ──────────────────────────────────────────────


class BusinessPreferencesView(APIView):
    """
    get: Returns the current tenant's business preferences.

    put: Updates the current tenant's business preferences.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.preferences.read"

    def get_service(self):
        return BusinessPreferencesService(
            prefs_repository=BusinessPreferencesRepository()
        )

    def get(self, request):
        tenant_id = request.actor.tenant_id
        service = self.get_service()
        prefs = service.get_preferences(tenant_id)
        if not prefs:
            return Response({"data": None}, status=status.HTTP_200_OK)
        serializer = BusinessPreferencesSerializer(prefs)
        return Response({"data": serializer.data})

    def put(self, request):
        tenant_id = request.actor.tenant_id
        serializer = BusinessPreferencesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = self.get_service()
        existing = service.get_preferences(tenant_id)

        if existing:
            # Merge validated data into existing entity
            for attr, value in serializer.validated_data.items():
                setattr(existing, attr, value)
            updated = service.update_preferences(existing)
        else:
            # Create new preferences entity
            prefs = BusinessPreferencesEntity(
                tenant_id=tenant_id,
                **{
                    k: v
                    for k, v in serializer.validated_data.items()
                    if hasattr(BusinessPreferencesEntity, k)
                },
            )
            updated = service.update_preferences(prefs)

        return Response(
            {"data": BusinessPreferencesSerializer(updated).data},
            status=status.HTTP_200_OK,
        )


BusinessPreferencesView.put.required_permission = "platform.preferences.edit"


# ──────────────────────────────────────────────
# Branch
# ──────────────────────────────────────────────


class BranchListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of branches for the current company.

    post: Creates a new branch.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.branches.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code", "city", "province"]
    ordering_fields = ["name", "code", "created_at", "is_head_office"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BranchCreateSerializer
        return BranchListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        company_id = self.request.query_params.get("company_id")
        if not company_id:
            return Branch.objects.none()
        return Branch.objects.filter(
            tenant_id=tenant_id, company_id=company_id
        ).order_by("name")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        company_id = request.data.get("company_id")

        branch = BranchEntity(
            tenant_id=tenant_id,
            company_id=company_id,
            **serializer.validated_data,
        )

        service = BranchService(
            branch_repository=BranchRepository(),
            company_repository=CompanyRepository(),
        )
        created = service.create_branch(branch)

        return Response(
            {"data": BranchDetailSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


BranchListCreateView.create.required_permission = "platform.branches.create"


class BranchDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    get: Returns detailed information about a specific branch.

    put: Updates a specific branch.

    delete: Soft-deletes a specific branch.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.branches.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return BranchUpdateSerializer
        return BranchDetailSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return Branch.objects.filter(tenant_id=tenant_id)

    def perform_update(self, serializer):
        tenant_id = self.request.actor.tenant_id
        branch_id = self.kwargs.get("pk")
        service = BranchService(
            branch_repository=BranchRepository(),
            company_repository=CompanyRepository(),
        )
        existing = service.get_branch(branch_id, tenant_id)
        if not existing:
            from django.http import Http404

            raise Http404

        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)

        updated = service.update_branch(existing)
        return updated

    def perform_destroy(self, instance):
        tenant_id = self.request.actor.tenant_id
        branch_id = str(instance.id)
        service = BranchService(
            branch_repository=BranchRepository(),
            company_repository=CompanyRepository(),
        )
        service.delete_branch(branch_id, tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = self.perform_update(serializer)
        return Response(
            {"data": BranchDetailSerializer(updated).data},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"data": {"deleted": True}},
            status=status.HTTP_200_OK,
        )


BranchDetailView.update.required_permission = "platform.branches.edit"
BranchDetailView.destroy.required_permission = "platform.branches.delete"


# ──────────────────────────────────────────────
# Warehouse
# ──────────────────────────────────────────────


class WarehouseListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of warehouses for a specific branch.

    post: Creates a new warehouse for a specific branch.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.warehouses.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code", "warehouse_type"]
    ordering_fields = ["name", "code", "created_at", "warehouse_type"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return WarehouseCreateSerializer
        return WarehouseListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        branch_id = self.kwargs.get("branch_id")
        return Warehouse.objects.filter(tenant_id=tenant_id, branch_id=branch_id).order_by(
            "name"
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        branch_id = self.kwargs.get("branch_id")

        warehouse = WarehouseEntity(
            tenant_id=tenant_id,
            branch_id=branch_id,
            **serializer.validated_data,
        )

        service = WarehouseService(warehouse_repository=WarehouseRepository())
        created = service.create_warehouse(warehouse)

        return Response(
            {"data": WarehouseDetailSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


WarehouseListCreateView.create.required_permission = "platform.warehouses.create"


class WarehouseDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    get: Returns detailed information about a specific warehouse.

    put: Updates a specific warehouse.

    delete: Soft-deletes a specific warehouse.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.warehouses.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return WarehouseUpdateSerializer
        return WarehouseDetailSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        branch_id = self.kwargs.get("branch_id")
        return Warehouse.objects.filter(tenant_id=tenant_id, branch_id=branch_id)

    def perform_update(self, serializer):
        tenant_id = self.request.actor.tenant_id
        warehouse_id = self.kwargs.get("pk")
        service = WarehouseService(warehouse_repository=WarehouseRepository())
        existing = service.get_warehouse(warehouse_id, tenant_id)
        if not existing:
            from django.http import Http404

            raise Http404

        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)

        updated = service.update_warehouse(existing)
        return updated

    def perform_destroy(self, instance):
        tenant_id = self.request.actor.tenant_id
        warehouse_id = str(instance.id)
        service = WarehouseService(warehouse_repository=WarehouseRepository())
        service.delete_warehouse(warehouse_id, tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = self.perform_update(serializer)
        return Response(
            {"data": WarehouseDetailSerializer(updated).data},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"data": {"deleted": True}},
            status=status.HTTP_200_OK,
        )


WarehouseDetailView.update.required_permission = "platform.warehouses.edit"
WarehouseDetailView.destroy.required_permission = "platform.warehouses.delete"


# ──────────────────────────────────────────────
# Currency
# ──────────────────────────────────────────────


class CurrencyListView(ListAPIView):
    """
    get: Returns a list of all active currencies.

    Currencies are global (not tenant-scoped) and read-only.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.currencies.read"
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name"]
    ordering = ["code"]

    def get_queryset(self):
        return Currency.objects.filter(is_active=True).order_by("code")

    def get_serializer_class(self):
        return CurrencySerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)


# ──────────────────────────────────────────────
# Tax Configuration
# ──────────────────────────────────────────────


class TaxConfigurationListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of tax configurations for the tenant.

    post: Creates a new tax configuration.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.taxes.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code", "tax_type", "tax_category"]
    ordering_fields = ["name", "rate", "effective_from", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TaxConfigurationCreateSerializer
        return TaxConfigurationListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        active_only = self.request.query_params.get("active_only", "true").lower() == "true"
        qs = TaxConfiguration.objects.filter(tenant_id=tenant_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.order_by("name")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from datetime import datetime

        tenant_id = request.actor.tenant_id

        tax = TaxConfigurationEntity(
            tenant_id=tenant_id,
            name=serializer.validated_data["name"],
            code=serializer.validated_data["code"],
            tax_type=serializer.validated_data["tax_type"],
            tax_category=serializer.validated_data["tax_category"],
            rate=float(serializer.validated_data["rate"]),
            is_recoverable=serializer.validated_data.get("is_recoverable", False),
            is_default=serializer.validated_data.get("is_default", False),
            effective_from=serializer.validated_data.get("effective_from", datetime.now()),
        )

        service = TaxConfigurationService(
            tax_repository=TaxConfigurationRepository()
        )
        created = service.create_tax_config(tax)

        return Response(
            {"data": TaxConfigurationDetailSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


TaxConfigurationListCreateView.create.required_permission = "platform.taxes.create"


class TaxConfigurationDetailView(RetrieveAPIView, UpdateAPIView):
    """
    get: Returns detailed information about a specific tax configuration.

    put: Updates a specific tax configuration (creates new version for history).
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.taxes.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return TaxConfigurationUpdateSerializer
        return TaxConfigurationDetailSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return TaxConfiguration.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id

        # Build updated tax config entity with versioning
        tax = TaxConfigurationEntity(
            id=str(instance.id),
            tenant_id=tenant_id,
            name=serializer.validated_data.get("name", instance.name),
            code=serializer.validated_data.get("code", instance.code),
            tax_type=serializer.validated_data.get("tax_type", instance.tax_type),
            tax_category=serializer.validated_data.get(
                "tax_category", instance.tax_category
            ),
            rate=float(serializer.validated_data.get("rate", instance.rate)),
            is_recoverable=serializer.validated_data.get(
                "is_recoverable", instance.is_recoverable
            ),
            is_default=serializer.validated_data.get("is_default", instance.is_default),
        )

        service = TaxConfigurationService(
            tax_repository=TaxConfigurationRepository()
        )
        updated = service.update_tax_config(tax)

        return Response(
            {"data": TaxConfigurationDetailSerializer(updated).data},
            status=status.HTTP_200_OK,
        )


TaxConfigurationDetailView.update.required_permission = "platform.taxes.edit"


# ──────────────────────────────────────────────
# Fiscal Year
# ──────────────────────────────────────────────


class FiscalYearListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of fiscal years for the tenant.

    post: Creates a new fiscal year.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.fiscal-years.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "status"]
    ordering_fields = ["name", "start_date", "end_date", "status", "created_at"]
    ordering = ["-start_date"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return FiscalYearCreateSerializer
        return FiscalYearListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        status_filter = self.request.query_params.get("status")
        qs = FiscalYear.objects.filter(tenant_id=tenant_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by("-start_date")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id

        fiscal_year = FiscalYearEntity(
            tenant_id=tenant_id,
            name=serializer.validated_data["name"],
            start_date=serializer.validated_data["start_date"],
            end_date=serializer.validated_data["end_date"],
            status=serializer.validated_data.get("status", "open"),
        )

        service = FiscalYearService(
            fiscal_year_repository=FiscalYearRepository()
        )
        created = service.create_fiscal_year(fiscal_year)

        return Response(
            {"data": FiscalYearDetailSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


FiscalYearListCreateView.create.required_permission = "platform.fiscal-years.create"


class FiscalYearDetailView(RetrieveAPIView):
    """
    get: Returns detailed information about a specific fiscal year.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.fiscal-years.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return FiscalYearDetailSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return FiscalYear.objects.filter(tenant_id=tenant_id)


class FiscalYearCloseView(APIView):
    """
    post: Closes a specific fiscal year.

    Once closed, the fiscal year cannot be reopened.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.fiscal-years.close"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = FiscalYearService(fiscal_year_repository=FiscalYearRepository())
        closed = service.close_fiscal_year(pk, tenant_id)
        if not closed:
            return _error_response(
                "Fiscal year not found or already closed.",
                code="FISCAL_YEAR_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"data": FiscalYearDetailSerializer(closed).data},
            status=status.HTTP_200_OK,
        )


# ──────────────────────────────────────────────
# Number Sequence
# ──────────────────────────────────────────────


class NumberSequenceListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of number sequences for the tenant.

    post: Creates a new number sequence.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.number-sequences.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "prefix"]
    ordering_fields = ["name", "current_number", "reset_policy", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return NumberSequenceCreateSerializer
        return NumberSequenceListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return NumberSequence.objects.filter(tenant_id=tenant_id).order_by("name")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id

        seq = NumberSequenceEntity(
            tenant_id=tenant_id,
            name=serializer.validated_data["name"],
            prefix=serializer.validated_data.get("prefix", ""),
            suffix=serializer.validated_data.get("suffix", ""),
            padding_length=serializer.validated_data.get("padding_length", 6),
            reset_policy=serializer.validated_data.get("reset_policy", "never"),
        )

        # Use repository directly for create since service has no create method
        created = NumberSequenceRepository().create(seq)

        return Response(
            {"data": NumberSequenceDetailSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


NumberSequenceListCreateView.create.required_permission = (
    "platform.number-sequences.create"
)


class NumberSequenceDetailView(RetrieveAPIView):
    """
    get: Returns detailed information about a specific number sequence.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.number-sequences.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return NumberSequenceDetailSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return NumberSequence.objects.filter(tenant_id=tenant_id)


class NumberSequenceNextView(APIView):
    """
    post: Gets the next formatted number in a sequence.

    Atomic operation via select_for_update.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.number-sequences.use"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = NumberSequenceService(
            number_sequence_repository=NumberSequenceRepository()
        )

        # Get the sequence to find its name
        seq = NumberSequenceRepository().get_by_id(pk, tenant_id)
        if not seq:
            return _error_response(
                "Number sequence not found.",
                code="SEQUENCE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        formatted = service.get_next_number(tenant_id, seq.name)
        return Response(
            {"data": {"formatted_number": formatted}},
            status=status.HTTP_200_OK,
        )


class NumberSequenceResetView(APIView):
    """
    post: Resets a number sequence back to 1.

    Emits a NumberSequenceReset domain event.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.number-sequences.reset"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = NumberSequenceService(
            number_sequence_repository=NumberSequenceRepository()
        )

        seq = NumberSequenceRepository().get_by_id(pk, tenant_id)
        if not seq:
            return _error_response(
                "Number sequence not found.",
                code="SEQUENCE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        success = service.reset_sequence(tenant_id, seq.name)
        return Response(
            {"data": {"success": success}},
            status=status.HTTP_200_OK,
        )


# ──────────────────────────────────────────────
# Stored File
# ──────────────────────────────────────────────


class StoredFileListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of stored files filtered by entity type and ID.

    post: Creates a new stored file metadata record.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "platform.files.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["original_filename", "mime_type", "module"]
    ordering_fields = ["uploaded_at", "original_filename", "file_size"]
    ordering = ["-uploaded_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StoredFileCreateSerializer
        return StoredFileListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        entity_type = self.request.query_params.get("entity_type")
        entity_id = self.request.query_params.get("entity_id")
        qs = StoredFile.objects.filter(tenant_id=tenant_id)
        if entity_type:
            qs = qs.filter(entity_type=entity_type)
        if entity_id:
            qs = qs.filter(entity_id=entity_id)
        return qs.order_by("-uploaded_at")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        user_id = str(request.user.id)

        stored_file = StoredFileEntity(
            tenant_id=tenant_id,
            uploaded_by=user_id,
            **serializer.validated_data,
        )

        service = StoredFileService(
            stored_file_repository=StoredFileRepository()
        )
        created = service.create_file(stored_file)

        return Response(
            {"data": StoredFileListSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


StoredFileListCreateView.create.required_permission = "platform.files.create"