from decimal import Decimal
import pytest
from packaging.models import Product, Box
from packaging.services import (
    can_product_fit,
    calculate_total_weight,
    calculate_total_volume,
    evaluate_boxes_feasibility,
    select_best_box,
    recommend_box,
    MockAIProvider,
    AIRecommendationService,
)


@pytest.mark.django_db
class TestBoxSelectionEngine:

    def test_exact_dimension_fit(self):
        # Product 10x10x10 fits inside Box 10x10x10
        assert can_product_fit(
            Decimal("10.00"), Decimal("10.00"), Decimal("10.00"),
            Decimal("10.00"), Decimal("10.00"), Decimal("10.00")
        ) is True

    def test_rotation_required_for_fit(self):
        # Product default L=30, W=10, H=5 does not fit Box L=15, W=35, H=10 without rotation,
        # but rotated W=10 <= L=15, L=30 <= W=35, H=5 <= H=10 fits!
        assert can_product_fit(
            Decimal("30.00"), Decimal("10.00"), Decimal("5.00"),
            Decimal("15.00"), Decimal("35.00"), Decimal("10.00")
        ) is True

    def test_exact_max_weight(self):
        product = Product.objects.create(
            name="Max Weight Item", length=Decimal("5"), width=Decimal("5"), height=Decimal("5"), weight=Decimal("5.00")
        )
        box = Box.objects.create(
            name="Max Weight Box", internal_length=Decimal("10"), internal_width=Decimal("10"), internal_height=Decimal("10"),
            max_weight=Decimal("5.00"), cost=Decimal("10.00")
        )
        items = [{"product": product, "quantity": 1}]
        feasible, _ = evaluate_boxes_feasibility(items, boxes=[box])
        assert len(feasible) == 1
        assert feasible[0] == box

    def test_weight_exceeded(self):
        product = Product.objects.create(
            name="Heavy Item", length=Decimal("5"), width=Decimal("5"), height=Decimal("5"), weight=Decimal("5.01")
        )
        box = Box.objects.create(
            name="Weight Constrained Box", internal_length=Decimal("10"), internal_width=Decimal("10"), internal_height=Decimal("10"),
            max_weight=Decimal("5.00"), cost=Decimal("10.00")
        )
        items = [{"product": product, "quantity": 1}]
        feasible, analysis = evaluate_boxes_feasibility(items, boxes=[box])
        assert len(feasible) == 0
        assert analysis[0]["status"] == "rejected"
        assert any("Maximum weight" in reason for reason in analysis[0]["reasons"])

    def test_exact_volume(self):
        product = Product.objects.create(
            name="Cube Item", length=Decimal("10"), width=Decimal("10"), height=Decimal("10"), weight=Decimal("1.00")
        )
        box = Box.objects.create(
            name="Cube Box", internal_length=Decimal("10"), internal_width=Decimal("10"), internal_height=Decimal("10"),
            max_weight=Decimal("5.00"), cost=Decimal("10.00")
        )
        items = [{"product": product, "quantity": 1}]
        assert calculate_total_volume(items) == Decimal("1000.00")
        feasible, _ = evaluate_boxes_feasibility(items, boxes=[box])
        assert len(feasible) == 1

    def test_volume_exceeded(self):
        # Product volume 1000 cm³ x 2 qty = 2000 cm³ > Box volume 1500 cm³
        product = Product.objects.create(
            name="Volumetric Item", length=Decimal("10"), width=Decimal("10"), height=Decimal("10"), weight=Decimal("0.50")
        )
        box = Box.objects.create(
            name="Small Vol Box", internal_length=Decimal("15"), internal_width=Decimal("10"), internal_height=Decimal("10"),
            max_weight=Decimal("10.00"), cost=Decimal("15.00")
        )
        items = [{"product": product, "quantity": 2}] # Volume = 2000 cm³
        feasible, analysis = evaluate_boxes_feasibility(items, boxes=[box]) # Box vol = 1500 cm³
        assert len(feasible) == 0
        assert analysis[0]["status"] == "rejected"
        assert any("Total product volume" in reason for reason in analysis[0]["reasons"])

    def test_multiple_quantities(self):
        product = Product.objects.create(
            name="Small Item", length=Decimal("5"), width=Decimal("5"), height=Decimal("5"), weight=Decimal("1.25")
        )
        items = [{"product": product, "quantity": 4}]
        assert calculate_total_weight(items) == Decimal("5.00")
        assert calculate_total_volume(items) == Decimal("500.00")

    def test_same_cost_uses_smaller_volume(self):
        box1 = Box.objects.create(
            name="Big Box Same Cost", internal_length=Decimal("40"), internal_width=Decimal("40"), internal_height=Decimal("40"),
            max_weight=Decimal("10.00"), cost=Decimal("20.00")
        )
        box2 = Box.objects.create(
            name="Compact Box Same Cost", internal_length=Decimal("20"), internal_width=Decimal("20"), internal_height=Decimal("20"),
            max_weight=Decimal("10.00"), cost=Decimal("20.00")
        )
        feasible = [box1, box2]
        best_box = select_best_box(feasible, strategy="lowest_cost")
        # Both cost 20.00, box2 has volume 8000 < box1 volume 64000
        assert best_box == box2

    def test_ai_failure_uses_fallback(self):
        failing_provider = MockAIProvider(simulate_failure=True)
        context = {
            "recommended_box": "Medium Box",
            "cost": "30.00",
        }
        service = AIRecommendationService(provider=failing_provider)
        explanation = service.get_explanation(context)
        assert "Rule-based Recommendation" in explanation
        assert "Medium Box" in explanation

    def test_ai_provider_is_mocked(self):
        provider = MockAIProvider()
        context = {
            "recommended_box": "Small Box",
            "cost": "15.00",
            "weight_utilization": "50.00%",
            "volume_utilization": "40.00%"
        }
        explanation = provider.generate_explanation(context)
        assert "AI Recommendation" in explanation
        assert "Small Box" in explanation
        assert "₹15.00" in explanation

    def test_no_suitable_box(self):
        product = Product.objects.create(
            name="Giant Item", length=Decimal("100"), width=Decimal("100"), height=Decimal("100"), weight=Decimal("50.00")
        )
        Box.objects.create(
            name="Tiny Box", internal_length=Decimal("10"), internal_width=Decimal("10"), internal_height=Decimal("10"),
            max_weight=Decimal("5.00"), cost=Decimal("5.00")
        )
        items = [{"product": product, "quantity": 1}]
        res = recommend_box(items)
        assert res["recommendation"] is None
        assert len(res["evaluated_boxes"]) == 1
        assert res["evaluated_boxes"][0]["status"] == "rejected"
