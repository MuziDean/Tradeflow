"""
API URL routing for the Platform module.

Per Backend Engineering Standards §6.7: Versioned from day one (/v1/).
Mounted at /api/v1/company/ in config/api_urls.py.
"""

from django.urls import path

from apps.platform.api.views import (
    BranchDetailView,
    BranchListCreateView,
    BusinessPreferencesView,
    CompanyProfileView,
    CurrencyListView,
    FiscalYearCloseView,
    FiscalYearDetailView,
    FiscalYearListCreateView,
    NumberSequenceDetailView,
    NumberSequenceListCreateView,
    NumberSequenceNextView,
    NumberSequenceResetView,
    StoredFileListCreateView,
    TaxConfigurationDetailView,
    TaxConfigurationListCreateView,
    TenantInfoView,
    WarehouseDetailView,
    WarehouseListCreateView,
)

urlpatterns = [
    # Tenant
    path("", TenantInfoView.as_view(), name="tenant-info"),
    # Company Profile
    path("profile/", CompanyProfileView.as_view(), name="company-profile"),
    # Business Preferences
    path(
        "preferences/",
        BusinessPreferencesView.as_view(),
        name="business-preferences",
    ),
    # Branches
    path("branches/", BranchListCreateView.as_view(), name="branch-list-create"),
    path(
        "branches/<uuid:pk>/",
        BranchDetailView.as_view(),
        name="branch-detail",
    ),
    # Warehouses (nested under branches)
    path(
        "branches/<uuid:branch_id>/warehouses/",
        WarehouseListCreateView.as_view(),
        name="warehouse-list-create",
    ),
    path(
        "branches/<uuid:branch_id>/warehouses/<uuid:pk>/",
        WarehouseDetailView.as_view(),
        name="warehouse-detail",
    ),
    # Currencies
    path("currencies/", CurrencyListView.as_view(), name="currency-list"),
    # Tax Configurations
    path(
        "taxes/",
        TaxConfigurationListCreateView.as_view(),
        name="tax-list-create",
    ),
    path(
        "taxes/<uuid:pk>/",
        TaxConfigurationDetailView.as_view(),
        name="tax-detail",
    ),
    # Fiscal Years
    path(
        "fiscal-years/",
        FiscalYearListCreateView.as_view(),
        name="fiscal-year-list-create",
    ),
    path(
        "fiscal-years/<uuid:pk>/",
        FiscalYearDetailView.as_view(),
        name="fiscal-year-detail",
    ),
    path(
        "fiscal-years/<uuid:pk>/close/",
        FiscalYearCloseView.as_view(),
        name="fiscal-year-close",
    ),
    # Number Sequences
    path(
        "number-sequences/",
        NumberSequenceListCreateView.as_view(),
        name="number-sequence-list-create",
    ),
    path(
        "number-sequences/<uuid:pk>/",
        NumberSequenceDetailView.as_view(),
        name="number-sequence-detail",
    ),
    path(
        "number-sequences/<uuid:pk>/next/",
        NumberSequenceNextView.as_view(),
        name="number-sequence-next",
    ),
    path(
        "number-sequences/<uuid:pk>/reset/",
        NumberSequenceResetView.as_view(),
        name="number-sequence-reset",
    ),
    # Stored Files
    path("files/", StoredFileListCreateView.as_view(), name="file-list-create"),
]