from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_strictly_positive(value):
    """Ensure a Decimal value is strictly greater than 0."""
    if value is None or Decimal(str(value)) <= Decimal('0'):
        raise ValidationError(_("Value must be strictly greater than zero."))


def validate_non_negative(value):
    """Ensure a Decimal value is greater than or equal to 0."""
    if value is None or Decimal(str(value)) < Decimal('0'):
        raise ValidationError(_("Value must be greater than or equal to zero."))


def validate_positive_quantity(value):
    """Ensure an integer quantity is strictly greater than 0."""
    if value is None or int(value) <= 0:
        raise ValidationError(_("Quantity must be a positive integer greater than zero."))
