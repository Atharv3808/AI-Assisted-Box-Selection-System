from decimal import Decimal, ROUND_HALF_UP
import itertools
from typing import List, Dict, Any, Tuple, Optional
from packaging.models import Product, Box


def round_decimal(value: Decimal, places: int = 2) -> Decimal:
    """Helper to round Decimal to fixed places."""
    return Decimal(str(value)).quantize(Decimal('1.' + '0' * places), rounding=ROUND_HALF_UP)


def calculate_total_weight(items: List[Dict[str, Any]]) -> Decimal:
    """
    Calculate the total weight of order items in kg.
    items: list of dicts with 'product' (Product instance) and 'quantity' (int).
    """
    total = Decimal('0.00')
    for item in items:
        product: Product = item['product']
        quantity = Decimal(str(item['quantity']))
        total += Decimal(str(product.weight)) * quantity
    return round_decimal(total, 2)


def calculate_total_volume(items: List[Dict[str, Any]]) -> Decimal:
    """
    Calculate the total volume of order items in cm³.
    items: list of dicts with 'product' (Product instance) and 'quantity' (int).
    """
    total = Decimal('0.00')
    for item in items:
        product: Product = item['product']
        quantity = Decimal(str(item['quantity']))
        total += product.volume * quantity
    return round_decimal(total, 2)


def get_product_orientations(length: Decimal, width: Decimal, height: Decimal) -> List[Tuple[Decimal, Decimal, Decimal]]:
    """
    Generate all 6 3D permutations (rotations) of product dimensions.
    Returns list of (L, W, H) tuples.
    """
    dims = (Decimal(str(length)), Decimal(str(width)), Decimal(str(height)))
    return list(set(itertools.permutations(dims)))


def can_product_fit(
    p_len: Decimal, p_wid: Decimal, p_hgt: Decimal,
    b_len: Decimal, b_wid: Decimal, b_hgt: Decimal
) -> bool:
    """
    Check if a product fits in a box considering all 6 3D rotation permutations.
    A product fits if at least one orientation satisfies:
    p_len <= b_len and p_wid <= b_wid and p_hgt <= b_hgt.
    """
    orientations = get_product_orientations(p_len, p_wid, p_hgt)
    b_len, b_wid, b_hgt = Decimal(str(b_len)), Decimal(str(b_wid)), Decimal(str(b_hgt))

    for l, w, h in orientations:
        if l <= b_len and w <= b_wid and h <= b_hgt:
            return True
    return False


def evaluate_boxes_feasibility(
    items: List[Dict[str, Any]],
    boxes: Optional[List[Box]] = None
) -> Tuple[List[Box], List[Dict[str, Any]]]:
    """
    Evaluate all boxes against feasibility rules:
    1. Every individual product fits dimensionally (checking 6 rotation permutations).
    2. Total order weight <= box max weight.
    3. Total product volume <= box internal volume.

    Returns (feasible_boxes, evaluated_boxes_analysis).
    """
    if boxes is None:
        boxes = list(Box.objects.all())

    total_weight = calculate_total_weight(items)
    total_volume = calculate_total_volume(items)

    feasible_boxes: List[Box] = []
    evaluated_boxes_analysis: List[Dict[str, Any]] = []

    for box in boxes:
        reasons: List[str] = []
        weight_passed = True
        volume_passed = True
        dimensional_passed = True

        # Rule 1: Max Weight Check
        if total_weight > box.max_weight:
            weight_passed = False
            reasons.append(
                f"Maximum weight is {box.max_weight:.2f} kg but order weight is {total_weight:.2f} kg"
            )

        # Rule 2: Volume Check
        if total_volume > box.internal_volume:
            volume_passed = False
            reasons.append(
                f"Total product volume is {total_volume:.2f} cm³ but box internal volume is {box.internal_volume:.2f} cm³"
            )

        # Rule 3: Dimensional Check for each product in order
        for item in items:
            product: Product = item['product']
            if not can_product_fit(
                product.length, product.width, product.height,
                box.internal_length, box.internal_width, box.internal_height
            ):
                dimensional_passed = False
                reasons.append(
                    f"Product '{product.name}' ({product.length}x{product.width}x{product.height} cm) "
                    f"exceeds box dimensions ({box.internal_length}x{box.internal_width}x{box.internal_height} cm) in all orientations"
                )

        status_str = "feasible" if not reasons else "rejected"
        if not reasons:
            feasible_boxes.append(box)

        evaluated_boxes_analysis.append({
            "box": box.name,
            "box_id": box.id,
            "cost": str(box.cost),
            "status": status_str,
            "dimensional_check": "passed" if dimensional_passed else "failed",
            "weight_check": "passed" if weight_passed else "failed",
            "volume_check": "passed" if volume_passed else "failed",
            "reasons": reasons
        })

    return feasible_boxes, evaluated_boxes_analysis


def select_best_box(feasible_boxes: List[Box], strategy: str = "lowest_cost") -> Optional[Box]:
    """
    Selection strategy to pick the best box from feasible candidates.
    Primary: Lowest cost
    Tie-breaker: Smaller internal volume
    """
    if not feasible_boxes:
        return None

    if strategy == "lowest_cost":
        return min(feasible_boxes, key=lambda b: (b.cost, b.internal_volume))
    
    # Fallback to default strategy
    return min(feasible_boxes, key=lambda b: (b.cost, b.internal_volume))


class BaseAIProvider:
    """Abstract interface for AI recommendation explanations."""
    def generate_explanation(self, context: Dict[str, Any]) -> str:
        raise NotImplementedError("Subclasses must implement generate_explanation.")


class MockAIProvider(BaseAIProvider):
    """
    Mock AI Provider simulating an LLM response.
    Can be configured to raise an exception to test fallback logic.
    """
    def __init__(self, simulate_failure: bool = False):
        self.simulate_failure = simulate_failure

    def generate_explanation(self, context: Dict[str, Any]) -> str:
        if self.simulate_failure:
            raise RuntimeError("AI service temporarily unavailable")

        box_name = context.get('recommended_box', 'Box')
        cost = context.get('cost', '0.00')

        return f"{box_name} is recommended because it is the lowest-cost feasible box (₹{cost}) for this order."



class AIRecommendationService:
    """
    AI Recommendation Service wrapper.
    Evaluates AI provider output and falls back cleanly to rule-based explanation on error.
    """
    def __init__(self, provider: Optional[BaseAIProvider] = None):
        self.provider = provider or MockAIProvider()

    def get_explanation(self, context: Dict[str, Any]) -> str:
        try:
            return self.provider.generate_explanation(context)
        except Exception as e:
            return self.generate_fallback_explanation(context)

    @staticmethod
    def generate_fallback_explanation(context: Dict[str, Any]) -> str:
        """Deterministic rule-based explanation fallback."""
        box_name = context.get('recommended_box', 'Box')
        cost = context.get('cost', '0.00')
        return f"Rule-based Recommendation: {box_name} selected as the lowest-cost box (₹{cost}) satisfying weight and dimension constraints."


def recommend_box(items: List[Dict[str, Any]], ai_provider: Optional[BaseAIProvider] = None) -> Dict[str, Any]:
    """
    Main orchestrator function for box recommendation API.
    1. Feasibility Engine
    2. Selection Strategy
    3. Metrics & Utilization
    4. AI / Fallback Explanation
    """
    total_weight = calculate_total_weight(items)
    total_volume = calculate_total_volume(items)

    feasible_boxes, evaluated_boxes = evaluate_boxes_feasibility(items)
    selected_box = select_best_box(feasible_boxes, strategy="lowest_cost")

    if not selected_box:
        return {
            "recommendation": None,
            "reason": "No suitable box found satisfying order constraints.",
            "order_summary": {
                "total_weight": str(total_weight),
                "total_volume": str(total_volume)
            },
            "utilization": None,
            "evaluated_boxes": evaluated_boxes
        }

    # Calculate utilization
    weight_util = (total_weight / selected_box.max_weight * Decimal('100')) if selected_box.max_weight > Decimal('0') else Decimal('0')
    vol_util = (total_volume / selected_box.internal_volume * Decimal('100')) if selected_box.internal_volume > Decimal('0') else Decimal('0')

    weight_util_str = f"{weight_util:.2f}%"
    vol_util_str = f"{vol_util:.2f}%"

    ai_context = {
        "recommended_box": selected_box.name,
        "cost": str(selected_box.cost),
        "total_weight": str(total_weight),
        "total_volume": str(total_volume),
        "weight_utilization": weight_util_str,
        "volume_utilization": vol_util_str,
        "feasible_boxes_count": len(feasible_boxes)
    }

    ai_service = AIRecommendationService(provider=ai_provider)
    reason = ai_service.get_explanation(ai_context)

    return {
        "recommendation": {
            "box_id": selected_box.id,
            "box_name": selected_box.name,
            "cost": str(selected_box.cost),
            "dimensions": f"{selected_box.internal_length}x{selected_box.internal_width}x{selected_box.internal_height} cm",
            "max_weight": f"{selected_box.max_weight} kg"
        },
        "reason": reason,
        "order_summary": {
            "total_weight": str(total_weight),
            "total_volume": str(total_volume)
        },
        "utilization": {
            "weight": weight_util_str,
            "volume": vol_util_str
        },
        "evaluated_boxes": evaluated_boxes
    }
