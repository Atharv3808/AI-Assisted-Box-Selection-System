from decimal import Decimal
import pytest
from django.core.exceptions import ValidationError
from packaging.models import Product, Box, Order, OrderItem


@pytest.mark.django_db
class TestPackagingModels:

    def test_valid_product(self):
        product = Product.objects.create(
            name="Test Product",
            length=Decimal("10.00"),
            width=Decimal("5.00"),
            height=Decimal("2.00"),
            weight=Decimal("1.50")
        )
        assert product.id is not None
        assert str(product) == "Test Product (10.00x5.00x2.00 cm, 1.50 kg)"
        assert product.volume == Decimal("100.00")

    def test_invalid_dimensions(self):
        product = Product(
            name="Invalid Dim Product",
            length=Decimal("0.00"),
            width=Decimal("-5.00"),
            height=Decimal("2.00"),
            weight=Decimal("1.00")
        )
        with pytest.raises(ValidationError):
            product.full_clean()

    def test_invalid_weight(self):
        product = Product(
            name="Negative Weight Product",
            length=Decimal("10.00"),
            width=Decimal("5.00"),
            height=Decimal("2.00"),
            weight=Decimal("-1.00")
        )
        with pytest.raises(ValidationError):
            product.full_clean()

    def test_valid_box(self):
        box = Box.objects.create(
            name="Test Box",
            internal_length=Decimal("20.00"),
            internal_width=Decimal("15.00"),
            internal_height=Decimal("10.00"),
            max_weight=Decimal("5.00"),
            cost=Decimal("12.50")
        )
        assert box.id is not None
        assert box.internal_volume == Decimal("3000.00")

    def test_invalid_box_values(self):
        box = Box(
            name="Invalid Box",
            internal_length=Decimal("10.00"),
            internal_width=Decimal("10.00"),
            internal_height=Decimal("10.00"),
            max_weight=Decimal("-2.00"),
            cost=Decimal("-5.00")
        )
        with pytest.raises(ValidationError):
            box.full_clean()

    def test_order_item_quantity(self):
        product = Product.objects.create(
            name="Sample Product",
            length=Decimal("5.00"),
            width=Decimal("5.00"),
            height=Decimal("5.00"),
            weight=Decimal("0.50")
        )
        order = Order.objects.create()
        item = OrderItem(order=order, product=product, quantity=0)
        with pytest.raises(ValidationError):
            item.full_clean()
