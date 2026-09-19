# Test Output

Run:

```bash
pytest packaging/tests/ -v
```

## Local Terminal Execution Output

```text
 
===================================== test session starts ======================================
platform darwin -- Python 3.12.5, pytest-8.3.2, pluggy-1.6.0 -- /usr/local/bin/python3
cachedir: .pytest_cache
django: version: 5.1.12, settings: config.settings (from ini)
rootdir: /Users/atharvshinde/AI-Assisted-Box-Selection-System/AI-Assisted-Box-Selection-System
configfile: pytest.ini
plugins: asyncio-0.23.7, anyio-4.13.0, cov-5.0.0, Faker-37.8.0, django-4.9.0, requests-mock-1.12.1
asyncio: mode=Mode.STRICT
collected 23 items                                                                             

packaging/tests/test_api.py::TestRecommendBoxAPI::test_successful_recommendation PASSED  [  4%]
packaging/tests/test_api.py::TestRecommendBoxAPI::test_empty_order PASSED                [  8%]
packaging/tests/test_api.py::TestRecommendBoxAPI::test_invalid_product PASSED            [ 13%]
packaging/tests/test_api.py::TestRecommendBoxAPI::test_invalid_quantity PASSED           [ 17%]
packaging/tests/test_api.py::TestRecommendBoxAPI::test_no_suitable_box_api PASSED        [ 21%]
packaging/tests/test_api.py::TestRecommendBoxAPI::test_api_root PASSED                   [ 26%]
packaging/tests/test_models.py::TestPackagingModels::test_valid_product PASSED           [ 30%]
packaging/tests/test_models.py::TestPackagingModels::test_invalid_dimensions PASSED      [ 34%]
packaging/tests/test_models.py::TestPackagingModels::test_invalid_weight PASSED          [ 39%]
packaging/tests/test_models.py::TestPackagingModels::test_valid_box PASSED               [ 43%]
packaging/tests/test_models.py::TestPackagingModels::test_invalid_box_values PASSED      [ 47%]
packaging/tests/test_models.py::TestPackagingModels::test_order_item_quantity PASSED     [ 52%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_exact_dimension_fit PASSED [ 56%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_rotation_required_for_fit PASSED [ 60%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_exact_max_weight PASSED  [ 65%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_weight_exceeded PASSED   [ 69%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_exact_volume PASSED      [ 73%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_volume_exceeded PASSED   [ 78%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_multiple_quantities PASSED [ 82%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_same_cost_uses_smaller_volume PASSED [ 86%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_ai_failure_uses_fallback PASSED [ 91%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_ai_provider_is_mocked PASSED [ 95%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_explicit_check_statuses PASSED [100%]

================================ 23 passed in 0.32s ========================
