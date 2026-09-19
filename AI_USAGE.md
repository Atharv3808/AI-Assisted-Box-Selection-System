# AI Usage

## 1. AI Tools Used

I used AI tools during this assignment mainly to help me understand the requirements, plan the project structure, review my approach, and speed up implementation.

### Tools used

- **ChatGPT** – Used for discussing the assignment requirements, architecture, AI integration approach, testing strategy, and reviewing design decisions.
- **AI coding assistant in my IDE** – Used to help generate and modify Django files, API code, business logic, tests, and configuration.

I did not use AI as a replacement for testing or verification. I reviewed the generated code and tested the final implementation locally.

---

## 2. Prompts I Gave

Some of the main prompts/requests I used during development were:

### Understanding the assignment

> Analyze this Django hiring assignment and explain how I should design and implement it. Give me the important development steps, architecture, models, API and testing requirements.

### AI integration

> The assignment is called an "AI-Assisted Box Selection System". Explain how AI should actually be used in the project instead of just adding AI unnecessarily.

### Project implementation

> Create an implementation plan for a Django REST API that takes ecommerce order items and recommends the most suitable shipping box based on product dimensions, weight, volume and box cost.

### Architecture review

> Review this implementation plan and identify anything missing, unnecessary, or technically incorrect before implementation.

### Testing

> Define test cases for product dimensions, box dimensions, rotation, weight limits, volume limits, multiple products, cheapest box selection, tie-breakers, API validation and AI fallback.

I also used follow-up prompts to refine the architecture and clarify specific implementation decisions.

---

## 3. What Output I Accepted

I used AI-generated suggestions for several parts of the development process, including:

- Django project structure
- Database model design
- REST API structure
- Service-layer architecture
- Product dimension and rotation logic
- Weight and volume calculations
- Box feasibility checking
- Lowest-cost box selection
- Cost tie-breaker logic
- Rejection reasons
- API validation
- Test case planning
- GitHub Actions configuration
- Seed data structure
- Documentation structure

One important design decision I accepted was separating the system into:

```text
Request
   ↓
Validation
   ↓
Feasibility Engine
   ↓
Selection Strategy
   ↓
AI Explanation
   ↓
API Response
```

This made the core business logic easier to test and understand.

---

## 4. What Output I Rejected or Modified

I did not use all AI suggestions exactly as generated. I changed the design where I felt it was unnecessary or unreliable.

### AI should not perform the actual calculations

I rejected the idea of letting an LLM decide whether a product fits inside a box or whether the weight exceeds the box limit.

For example, calculations such as:

```text
7 kg <= 5 kg
```

should not depend on an LLM.

These calculations are handled by normal Python code.

### AI is used for explanation

The final design uses AI after the deterministic engine has evaluated the boxes.

The flow is:

```text
Python calculates feasibility
        ↓
Python selects the best valid box
        ↓
AI explains the recommendation
```

If the AI service is unavailable, the system generates a rule-based explanation instead.

### 3D packing limitation

I also avoided claiming that the system completely solves 3D packing.

The current implementation checks:

- Product orientation
- Product dimensions
- Total volume
- Total weight

This does not guarantee that multiple products can physically be arranged inside the box without overlapping.

I documented this limitation in the README.

---

## 5. Mistakes or Problems Found During AI-Assisted Development

One important issue I identified was the difference between **individual product fitting** and **actual multi-product packing**.

A product can individually fit inside a box, and the total volume can also be within the box volume, but the products may still not physically fit together.

Because of this, I documented the current implementation as a simplified feasibility model rather than claiming it is a complete 3D bin-packing solution.

Another important correction was keeping the actual box selection deterministic.

The final system does not ask an LLM:

> "Which box should I choose?"

Instead, Python evaluates the constraints and selects the lowest-cost feasible box. AI is used to provide the explanation.

I also made sure that an AI/API failure does not cause the entire application to fail. A deterministic fallback is provided.

---

## 6. How I Verified the Final Code

I verified the project by running the Django checks, database setup, seed command, automated tests and API manually.

### Django system check

```bash
python manage.py check
```

The check completed successfully without any system issues.

### Database migration

```bash
python manage.py migrate
```

The database was created and migrations completed successfully.

### Seed data

```bash
python manage.py seed_data
```

The command successfully created the sample products and shipping boxes.

### Automated tests

I ran:

```bash
pytest packaging/tests/ -v
```

The final test run completed with:

```text
23 passed in 0.32 seconds
```


The tests covered:

- Product validation
- Box validation
- Exact dimension fitting
- Product rotation
- Weight limits
- Volume limits
- Multiple quantities
- Cheapest feasible box
- Cost tie-breaker
- Rejection reasons
- AI provider mocking
- AI failure fallback
- API validation
- Successful recommendations
- No suitable box scenarios

### Manual API testing

I also started the Django development server and tested:

```text
POST /api/orders/recommend-box/
```

using a real JSON request.

I checked that the API returned the recommended box, order calculations, utilization values, AI explanation, and rejection reasons for boxes that were not suitable.

---

## Final Note

AI was used as a development assistant, but the important business rules were implemented and verified in Python.

The final design intentionally keeps physical calculations and box selection deterministic while using AI where it adds value: generating a clear explanation of the recommendation.