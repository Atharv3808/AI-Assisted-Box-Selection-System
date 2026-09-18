# Test Output

Run:

```bash
pytest packaging/tests/ -v
```

## Local Terminal Execution Output

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.4, pytest-8.4.1, pluggy-1.6.0 -- /opt/anaconda3/bin/python
cachedir: .pytest_cache
django: version: 5.1.15, settings: config.settings (from ini)
rootdir: /Users/atharvshinde/AI-Assisted-Box-Selection-System/AI-Assisted-Box-Selection-System
configfile: pytest.ini
plugins: django-4.12.0, cov-7.1.0, asyncio-1.4.0, anyio-4.10.0, langsmith-0.4.12
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 23 items

packaging/tests/test_api.py::TestRecommendBoxAPI::test_successful_recommendation PASSED [  4%]
packaging/tests/test_api.py::TestRecommendBoxAPI::test_empty_order PASSED [  8%]
packaging/tests/test_api.py::TestRecommendBoxAPI::test_invalid_product PASSED [ 13%]
packaging/tests/test_api.py::TestRecommendBoxAPI::test_invalid_quantity PASSED [ 17%]
packaging/tests/test_api.py::TestRecommendBoxAPI::test_no_suitable_box_api PASSED [ 21%]
packaging/tests/test_api.py::TestRecommendBoxAPI::test_api_root PASSED   [ 26%]
packaging/tests/test_models.py::TestPackagingModels::test_valid_product PASSED [ 30%]
packaging/tests/test_models.py::TestPackagingModels::test_invalid_dimensions PASSED [ 34%]
packaging/tests/test_models.py::TestPackagingModels::test_invalid_weight PASSED [ 39%]
packaging/tests/test_models.py::TestPackagingModels::test_valid_box PASSED [ 43%]
packaging/tests/test_models.py::TestPackagingModels::test_invalid_box_values PASSED [ 47%]
packaging/tests/test_models.py::TestPackagingModels::test_order_item_quantity PASSED [ 52%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_exact_dimension_fit PASSED [ 56%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_rotation_required_for_fit PASSED [ 60%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_exact_max_weight PASSED [ 65%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_weight_exceeded PASSED [ 69%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_exact_volume PASSED [ 73%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_volume_exceeded PASSED [ 78%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_multiple_quantities PASSED [ 82%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_same_cost_uses_smaller_volume PASSED [ 86%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_ai_failure_uses_fallback PASSED [ 91%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_ai_provider_is_mocked PASSED [ 95%]
packaging/tests/test_selection.py::TestBoxSelectionEngine::test_no_suitable_box PASSED [100%]

============================== 23 passed in 0.28s ==============================
```

