"""
Django models for the retail module.

Per Database Design: Sales, invoices, and retail-specific tables.
"""

from django.db import models

from infrastructure.db.base_model import TenantModel
from shared.ids.uuid import new_id_str


class Sale(TenantModel):
    """
    Django model for sales transactions.
    """

    branch_id = models.CharField(max_length=36, db_index=True)
    user_id = models.CharField(max_length=36, db_index=True)
    customer_id = models.CharField(max_length=36, db_index=True)
    invoice_number = models.CharField(max_length=50, unique=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, default="cash")
    status = models.CharField(max_length=20, default="completed")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "retail_sales"
        indexes = [
            models.Index(fields=["tenant_id", "created_at"]),
            models.Index(fields=["branch_id", "created_at"]),
        ]


class SaleItem(models.Model):
    """
    Django model for sale line items.
    """

    id = models.CharField(primary_key=True, max_length=36, default=new_id_str)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product_id = models.CharField(max_length=36, db_index=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "retail_sale_items"