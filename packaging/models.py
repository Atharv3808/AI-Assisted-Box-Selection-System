from decimal import Decimal
from django.db import models
from packaging.validators import (
    validate_strictly_positive,
    validate_non_negative,
    validate_positive_quantity,
)


class Product(models.Model):
    """
    Ecommerce Product model.
    Dimensions in cm, weight in kg.
    """
    name = models.CharField(max_length=255)
    length = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_strictly_positive]
    )
    width = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_strictly_positive]
    )
    height = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_strictly_positive]
    )
    weight = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_non_negative]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.length}x{self.width}x{self.height} cm, {self.weight} kg)"

    @property
    def volume(self) -> Decimal:
        """Returns product volume in cm³."""
        return Decimal(str(self.length)) * Decimal(str(self.width)) * Decimal(str(self.height))


class Box(models.Model):
    """
    Shipping Box model.
    Internal dimensions in cm, max_weight in kg, cost in INR.
    """
    name = models.CharField(max_length=255)
    internal_length = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_strictly_positive]
    )
    internal_width = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_strictly_positive]
    )
    internal_height = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_strictly_positive]
    )
    max_weight = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_non_negative]
    )
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_non_negative]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Boxes'
        ordering = ['cost', 'created_at']

    def __str__(self):
        return f"{self.name} ({self.internal_length}x{self.internal_width}x{self.internal_height} cm, Max: {self.max_weight} kg, ₹{self.cost})"

    @property
    def internal_volume(self) -> Decimal:
        """Returns box internal volume in cm³."""
        return Decimal(str(self.internal_length)) * Decimal(str(self.internal_width)) * Decimal(str(self.internal_height))


class Order(models.Model):
    """
    Ecommerce Order model.
    """
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} ({self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else 'New'})"


class OrderItem(models.Model):
    """
    Item within an Order referencing a Product and Quantity.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1, validators=[validate_positive_quantity])

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Order #{self.order_id})"
