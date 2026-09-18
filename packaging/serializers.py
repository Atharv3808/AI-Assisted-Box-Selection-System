from rest_framework import serializers
from packaging.models import Product


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class RecommendBoxRequestSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True, allow_empty=False)

    def validate_items(self, value):
        """Ensure all product_ids exist in DB and build structured product instances list."""
        if not value:
            raise serializers.ValidationError("Order items list cannot be empty.")

        product_ids = [item['product_id'] for item in value]
        existing_products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        validated_items = []
        for item in value:
            p_id = item['product_id']
            if p_id not in existing_products:
                raise serializers.ValidationError(f"Product with ID {p_id} does not exist.")
            validated_items.append({
                'product': existing_products[p_id],
                'quantity': item['quantity']
            })

        return validated_items
