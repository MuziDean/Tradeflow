"""
Standard pagination for TradeFlow API.

Per API Specification Section 10.4: Cursor-based pagination for large datasets;
offset pagination for small admin lists.
"""

from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Standard page-based pagination for list endpoints."""

    page_size = 50
    page_size_query_param = "per_page"
    max_page_size = 100
    page_query_param = "page"