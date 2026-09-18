from decimal import Decimal
from django.core.management.base import BaseCommand
from packaging.models import Product, Box


class Command(BaseCommand):
    help = "Seeds database with initial realistic products and boxes (idempotent)."

    def handle(self, *args, **options):
        products_data = [
            {"id": 1, "name": "Laptop", "length": Decimal("35.00"), "width": Decimal("25.00"), "height": Decimal("2.00"), "weight": Decimal("2.50")},
            {"id": 2, "name": "Phone", "length": Decimal("15.00"), "width": Decimal("8.00"), "height": Decimal("1.00"), "weight": Decimal("0.30")},
            {"id": 3, "name": "Book", "length": Decimal("22.00"), "width": Decimal("14.00"), "height": Decimal("3.00"), "weight": Decimal("0.60")},
            {"id": 4, "name": "Shoes", "length": Decimal("32.00"), "width": Decimal("20.00"), "height": Decimal("12.00"), "weight": Decimal("1.20")},
        ]

        boxes_data = [
            {"id": 1, "name": "Small Box", "internal_length": Decimal("20.00"), "internal_width": Decimal("15.00"), "internal_height": Decimal("10.00"), "max_weight": Decimal("5.00"), "cost": Decimal("15.00")},
            {"id": 2, "name": "Medium Box", "internal_length": Decimal("36.00"), "internal_width": Decimal("26.00"), "internal_height": Decimal("15.00"), "max_weight": Decimal("10.00"), "cost": Decimal("30.00")},
            {"id": 3, "name": "Large Box", "internal_length": Decimal("50.00"), "internal_width": Decimal("40.00"), "internal_height": Decimal("30.00"), "max_weight": Decimal("25.00"), "cost": Decimal("60.00")},
        ]

        p_created, p_updated = 0, 0
        for p in products_data:
            _, created = Product.objects.update_or_create(
                id=p["id"],
                defaults={
                    "name": p["name"],
                    "length": p["length"],
                    "width": p["width"],
                    "height": p["height"],
                    "weight": p["weight"],
                }
            )
            if created:
                p_created += 1
            else:
                p_updated += 1

        b_created, b_updated = 0, 0
        for b in boxes_data:
            _, created = Box.objects.update_or_create(
                id=b["id"],
                defaults={
                    "name": b["name"],
                    "internal_length": b["internal_length"],
                    "internal_width": b["internal_width"],
                    "internal_height": b["internal_height"],
                    "max_weight": b["max_weight"],
                    "cost": b["cost"],
                }
            )
            if created:
                b_created += 1
            else:
                b_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded database: Products ({p_created} created, {p_updated} updated), "
                f"Boxes ({b_created} created, {b_updated} updated)."
            )
        )
