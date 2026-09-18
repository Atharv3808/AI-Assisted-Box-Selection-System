from decimal import Decimal
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from packaging.models import Product, Box


@pytest.mark.django_db
class TestRecommendBoxAPI:

    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.client = APIClient()
        self.laptop = Product.objects.create(
            id=1, name="Laptop", length=Decimal("35.00"), width=Decimal("25.00"), height=Decimal("2.00"), weight=Decimal("2.50")
        )
        self.phone = Product.objects.create(
            id=2, name="Phone", length=Decimal("15.00"), width=Decimal("8.00"), height=Decimal("1.00"), weight=Decimal("0.30")
        )
        self.small_box = Box.objects.create(
            id=1, name="Small Box", internal_length=Decimal("20.00"), internal_width=Decimal("15.00"), internal_height=Decimal("10.00"),
            max_weight=Decimal("5.00"), cost=Decimal("15.00")
        )
        self.medium_box = Box.objects.create(
            id=2, name="Medium Box", internal_length=Decimal("36.00"), internal_width=Decimal("26.00"), internal_height=Decimal("15.00"),
            max_weight=Decimal("10.00"), cost=Decimal("30.00")
        )
        self.url = reverse('recommend-box')

    def test_successful_recommendation(self):
        # Phone (id=2) fits in Small Box (cost 15.00)
        payload = {
            "items": [
                {"product_id": 2, "quantity": 1}
            ]
        }
        response = self.client.post(self.url, payload, format='json')
        assert response.status_code == 200
        data = response.json()
        assert data["recommendation"]["box_id"] == self.small_box.id
        assert data["recommendation"]["box_name"] == "Small Box"
        assert "utilization" in data
        assert "order_summary" in data
        assert "evaluated_boxes" in data

    def test_empty_order(self):
        payload = {"items": []}
        response = self.client.post(self.url, payload, format='json')
        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_invalid_product(self):
        payload = {
            "items": [
                {"product_id": 999, "quantity": 1}
            ]
        }
        response = self.client.post(self.url, payload, format='json')
        assert response.status_code == 400
        data = response.json()
        assert "does not exist" in str(data)

    def test_invalid_quantity(self):
        payload = {
            "items": [
                {"product_id": 1, "quantity": 0}
            ]
        }
        response = self.client.post(self.url, payload, format='json')
        assert response.status_code == 400

    def test_no_suitable_box_api(self):
        # Laptop (id=1) length=35 cm x 10 qty exceeds weight (25kg > 10kg max weight) and volume
        payload = {
            "items": [
                {"product_id": 1, "quantity": 10}
            ]
        }
        response = self.client.post(self.url, payload, format='json')
        assert response.status_code == 422
        data = response.json()
        assert data["recommendation"] is None
        assert len(data["evaluated_boxes"]) > 0
        assert data["evaluated_boxes"][0]["status"] == "rejected"

    def test_api_root(self):
        root_url = reverse('api-root')
        response = self.client.get(root_url)
        assert response.status_code == 200
        data = response.json()
        assert data["system"] == "AI-Assisted Box Selection System"
        assert "/api/orders/recommend-box/" in data["endpoints"]["recommend_box"]

