# AI-Assisted Box Selection System

Production-oriented Django REST API that recommends the most suitable shipping box for ecommerce orders containing one or more products.

---

## Problem Statement

Ecommerce fulfilment operations need to select an appropriate shipping box for every order while satisfying physical constraints and minimizing packaging cost.

The system must consider:

- Product dimensions and weight
- Box internal dimensions and maximum weight
- 3D product rotations
- Total order volume
- Box cost
- Clear rejection reasons for unsuitable boxes

The goal is to provide a deterministic and explainable box recommendation while using AI where it adds value.

---

## Solution Overview

The **AI-Assisted Box Selection System** combines a deterministic physical evaluation engine with an AI-assisted explanation service.

### Core Approach

- **Deterministic rules guarantee physical feasibility.**
  All dimension, rotation, weight, and volume calculations are performed by Python.

- **Deterministic selection chooses the box.**
  Among feasible boxes, the system selects the lowest-cost box, using internal volume as the tie-breaker.

- **AI assists with explanation.**
  The AI service receives already-calculated metrics and candidate information and generates a natural-language explanation.

- **Fallback ensures reliability.**
  If the AI provider is unavailable, a deterministic rule-based explanation is returned instead.

This keeps the critical business logic independent of an LLM.

---

## Architecture

```text
                    POST /api/orders/recommend-box/
                                 │
                                 ▼
                        Request Validation
                                 │
                                 ▼
                      ┌──────────────────┐
                      │ Feasibility      │
                      │ Engine           │
                      │                  │
                      │ 6-Way Rotation   │
                      │ Weight Check     │
                      │ Volume Check     │
                      └────────┬─────────┘
                                 │
                         Feasible Candidates
                                 │
                                 ▼
                      Selection Strategy
                    lowest cost → volume tie
                                 │
                                 ▼
                   AI Recommendation Service
                      (Explanation Generator)
                                 │
                         AI provider available?
                           ↙             ↘
                         NO              YES
                          │                │
                   Rule-based            AI
                     fallback           output
                          └───────┬────────┘
                                  ▼
                           API Response
```

---

## Technology Stack

- **Python:** 3.12+
- **Framework:** Django 5.x
- **API:** Django REST Framework
- **Database:** SQLite
- **Testing:** pytest + pytest-django
- **CI:** GitHub Actions

### Units

| Measurement | Unit |
|---|---|
| Dimensions | centimeters (cm) |
| Weight | kilograms (kg) |
| Cost | Indian Rupees (INR ₹) |

---

## Project Structure

```text
AI-Assisted-Box-Selection-System/
│
├── manage.py
├── requirements.txt
├── pytest.ini
├── README.md
├── AI_USAGE.md
├── TEST_OUTPUT.md
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── packaging/
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── services.py
    ├── validators.py
    ├── views.py
    ├── urls.py
    │
    ├── management/
    │   └── commands/
    │       └── seed_data.py
    │
    └── tests/
        ├── test_models.py
        ├── test_selection.py
        └── test_api.py
```

---

## Data Model

The application uses four relational models.

### Product

Stores product information:

- `name`
- `length`
- `width`
- `height`
- `weight`
- `created_at`

### Box

Stores shipping box information:

- `name`
- `internal_length`
- `internal_width`
- `internal_height`
- `max_weight`
- `cost`
- `created_at`

### Order

Represents a customer order:

- `created_at`

### OrderItem

Connects products to orders:

- `order`
- `product`
- `quantity`

`DecimalField` is used for dimensions, weight, and cost to avoid unnecessary floating-point precision issues in business calculations.

---

## Box Selection Algorithm

### 1. Order Aggregation

The system first calculates the total order weight and volume.

```text
total_weight =
    Σ(product.weight × quantity)
```

```text
total_volume =
    Σ(product.length × product.width × product.height × quantity)
```

---

### 2. 6-Way Product Rotation

Each product is evaluated across all possible orthogonal orientations:

```text
(L, W, H)
(L, H, W)
(W, L, H)
(W, H, L)
(H, L, W)
(H, W, L)
```

A product fits when at least one orientation satisfies:

```text
product_length  ≤ box_length
product_width   ≤ box_width
product_height  ≤ box_height
```

Exact dimension matches are considered valid.

---

### 3. Feasibility Evaluation

A box is considered feasible when:

1. Every product can fit in at least one orientation.
2. Total order weight is within the box's maximum weight.
3. Total order volume is within the box's internal volume.

```text
total_weight ≤ box.max_weight
```

```text
total_volume ≤ box.internal_volume
```

For rejected boxes, the API provides specific reasons such as:

- Product dimension mismatch
- Total weight exceeds maximum box weight
- Total volume exceeds internal box volume

---

### 4. Selection Strategy

After feasibility evaluation, the system selects the recommended box using:

```text
Primary criteria:
    Lowest cost

Tie-breaker:
    Smallest internal volume
```

The selection logic is intentionally separated from feasibility evaluation so that additional strategies can be introduced later.

---

## AI-Assisted Architecture

The AI functionality is isolated inside the `AIRecommendationService`.

### What Python Handles

The deterministic Python layer handles:

- Product dimensions
- 6-way rotations
- Weight calculations
- Volume calculations
- Box feasibility
- Rejection reasons
- Box selection
- Utilization calculations

### What AI Handles

The AI layer receives verified information such as:

- Selected box
- Box cost
- Weight utilization
- Volume utilization
- Order totals
- Rejected box reasons

It then generates a concise natural-language explanation.

The AI is **not trusted with physical calculations or feasibility validation**.

For example, the system does not ask an LLM to determine whether:

```text
7 kg > 5 kg
```

Instead, Python performs that calculation and passes the verified result to the explanation layer.

### Fallback

If the AI provider fails, is unavailable, or returns an unusable response, the application falls back to a deterministic rule-based explanation.

This prevents an AI service failure from causing the box recommendation endpoint to fail.

---

## Business Rules

- Product dimensions must be greater than `0`.
- Box internal dimensions must be greater than `0`.
- Product weight must be greater than or equal to `0`.
- Box maximum weight must be greater than or equal to `0`.
- Box cost must be greater than or equal to `0`.
- Order item quantity must be a positive integer.
- Exact dimension matches are allowed.
- Exact weight limits are allowed.
- Exact volume limits are allowed.
- Every product must individually fit inside the selected box in at least one orientation.

---

## API

### Endpoint

```http
POST /api/orders/recommend-box/
```

### Request

```json
{
    "items": [
        {
            "product_id": 1,
            "quantity": 1
        },
        {
            "product_id": 2,
            "quantity": 2
        }
    ]
}
```

### Response

```json
{
    "recommendation": {
        "box_id": 2,
        "box_name": "Medium Box",
        "cost": "30.00",
        "dimensions": "36.00x26.00x15.00 cm",
        "max_weight": "10.00 kg"
    },
    "reason": "Medium Box is recommended because it is the lowest-cost feasible box (₹30.00) for this order.",
    "order_summary": {
        "total_weight": "3.10",
        "total_volume": "1990.00"
    },
    "utilization": {
        "weight": "31.00%",
        "volume": "14.17%"
    },
    "evaluated_boxes": [
        {
            "box": "Small Box",
            "box_id": 1,
            "cost": "15.00",
            "status": "rejected",
            "dimensional_check": "failed",
            "weight_check": "passed",
            "volume_check": "passed",
            "reasons": [
                "Product 'Laptop' (35.00x25.00x2.00 cm) exceeds box dimensions (20.00x15.00x10.00 cm) in all orientations"
            ]
        },
        {
            "box": "Medium Box",
            "box_id": 2,
            "cost": "30.00",
            "status": "feasible",
            "dimensional_check": "passed",
            "weight_check": "passed",
            "volume_check": "passed",
            "reasons": []
        }
    ]
}
```


---

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd AI-Assisted-Box-Selection-System
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply migrations

```bash
python manage.py migrate
```

### 4. Seed sample data

```bash
python manage.py seed_data
```

### 5. Start the development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

---

## Seed Data

The seed command creates sample products and shipping boxes:

### Products

| ID | Product | Dimensions | Weight |
|---:|---|---|---:|
| 1 | Laptop | 35 × 25 × 2 cm | 2.5 kg |
| 2 | Phone | 15 × 8 × 1 cm | 0.3 kg |
| 3 | Book | 22 × 14 × 3 cm | 0.6 kg |
| 4 | Shoes | 32 × 20 × 12 cm | 1.2 kg |

### Boxes

| ID | Box | Internal Dimensions | Max Weight | Cost |
|---:|---|---|---:|---:|
| 1 | Small Box | 20 × 15 × 10 cm | 5 kg | ₹15 |
| 2 | Medium Box | 36 × 26 × 15 cm | 10 kg | ₹30 |
| 3 | Large Box | 50 × 40 × 30 cm | 25 kg | ₹60 |

The seed command is designed to be safely re-runnable without unnecessarily creating duplicate sample records.

---

## Testing

Run the complete test suite:

```bash
pytest packaging/tests/ -v
```

The test suite covers:

- Model validation
- Exact dimension matches
- 3D rotation requirements
- Weight limits
- Volume limits
- Multiple quantities
- Lowest-cost selection
- Volume tie-breaker
- Rejection reasons
- AI provider mocking
- AI failure fallback
- API validation
- Invalid products
- Invalid quantities
- Orders with no suitable box

### Latest Test Run

```text
23 passed in 0.28s
```


Django system check:

```text
System check identified no issues.
```

Tests are also executed automatically through GitHub Actions.

---

## Design Decisions

### 1. Deterministic Feasibility

Physical feasibility is kept completely deterministic.

This makes the core business logic:

- predictable
- testable
- reproducible
- independent of external AI services

### 2. Separation of Responsibilities

The system separates:

```text
Feasibility Evaluation
        ↓
Box Selection
        ↓
Explanation Generation
```

This prevents the AI layer from becoming responsible for core business decisions that require exact calculations.

### 3. Strategy-Based Selection

The selection logic is implemented separately from feasibility evaluation.

The current strategy is:

```text
lowest_cost
```

with internal volume as the tie-breaker.

This allows future selection strategies to be added without rewriting the feasibility engine.

### 4. AI Failure Does Not Break Recommendations

The application can still return a valid deterministic recommendation when the AI service is unavailable.

---

## Assumptions

- Dimensions are measured in centimeters.
- Weight is measured in kilograms.
- Cost is measured in INR.
- Products can be freely rotated across the six orthogonal orientations.
- A single box is selected for the complete order.
- The current implementation evaluates individual product fit rather than calculating an exact spatial arrangement of all products.

---

## Limitations

> [!IMPORTANT]
> **Simplified 3D Packing Model**
>
> The current implementation does **not** solve exact multi-item 3D bin packing.
>
> It validates:
>
> - Individual product 6-way rotation fit
> - Total product volume
> - Total product weight
>
> However, individual product fitting + total volume fitting + weight fitting does **not** mathematically guarantee that multiple products can be physically arranged inside the box without overlapping.
>
> Exact multi-item spatial packing would require a dedicated 3D bin-packing algorithm.

---

## Future Improvements

1. **True 3D Bin Packing**
   - Add a dedicated 3D bin-packing algorithm or heuristic to verify the physical arrangement of multiple products.

2. **Multi-Box Shipments**
   - Allow large orders to be split across multiple boxes when no single box can accommodate the complete order.

3. **Dynamic AI Providers**
   - Connect OpenAI, Gemini, or another provider through environment-based configuration.

4. **Additional Selection Strategies**
   - Minimum volume
   - Minimum dimensional waste
   - Packaging efficiency
   - Multi-box optimization

5. **Production Infrastructure**
   - PostgreSQL
   - Authentication and authorization
   - Structured logging
   - Monitoring
   - Rate limiting
   - Containerized deployment

---

## AI Usage

AI assistance used during development is documented separately in:

```text
AI_USAGE.md
```

This document records:

- AI tools used
- Prompts provided
- Outputs accepted
- Outputs rejected or modified
- AI mistakes identified
- Verification performed on the final implementation

---

## Test Output

Detailed test execution information is available in:

```text
TEST_OUTPUT.md
```

---

## What Did You Learn?

So through this assignment I learned how to build a Django REST API with proper business logic.i learned how to use logic to separate box selection with dimensions weight and volume and cost. I use ai only as an assist layer and use logic to separate box . this assignment also help to enhance my automated testing with GitHub actions , handling test case and I learned that when using ai tools I should verify and test the generated code instead of accepting the code blindly 

---

## Chat Transcript

The required AI chat transcript is included separately as required by the assignment.