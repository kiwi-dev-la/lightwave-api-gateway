# Test-Driven Development (TDD) Guide for the Analytics API

This project follows TDD principles as described in [Pytest with Eric's TDD guide](https://pytest-with-eric.com/tdd/pytest-tdd/). This README provides guidance on how to use and extend the test suite.

## TDD Process (Red-Green-Refactor)

Test-Driven Development follows these steps:

1. **Write the Test (Red)**: First, write a test for a feature before implementing the feature itself.
2. **Write the Minimum Code (Green)**: Next, write just enough code to make the test pass.
3. **Run The Test (Green)**: Verify the code passes the test.
4. **Refactor/Improve Code (Refactor)**: Clean up the code while ensuring tests still pass.
5. **Repeat**: Continue with the next feature or enhancement.

## Running Tests

This project uses pytest for testing. We've set up several approaches to handle testing:

### Simple Tests (No Database)

These tests use a completely mocked environment to test basic route functionality:

```bash
# Run the simple tests
uv run pytest -v tests/test_simple.py
```

### Complete Tests (With Database Mocking)

These tests attempt to mock the database connections, but may not work in all environments:

```bash
# Run the without_db tests
uv run pytest -v tests/test_without_db.py
```

### Full Test Suite

To run all tests:

```bash
# Run all tests
uv run pytest

# With verbose output
uv run pytest -v
```

## Test Structure

We've organized tests by their complexity and dependence on external systems:

- `test_simple.py`: Completely mocked tests for basic endpoint functionality
- `test_without_db.py`: Tests that try to mock database connections
- `test_health.py`, `test_root.py`, etc.: Individual endpoint tests

## Adding New Tests

When adding new tests, follow these guidelines:

1. **Start Simple**: Begin with mocked tests that don't depend on external services
2. **Follow TDD**: Write the test first, then implement the feature
3. **Be Specific**: Test one thing at a time, keep tests focused and small
4. **Use Fixtures**: Leverage pytest fixtures for test setup and teardown

## Example TDD Workflow

Here's an example workflow for adding a new feature using TDD:

1. **Write a Test**: Create a test for the new feature (it will fail)
   ```python
   # tests/test_new_feature.py
   def test_new_feature(client):
       response = client.get("/new-feature")
       assert response.status_code == 200
       assert response.json() == {"feature": "implemented"}
   ```

2. **Run the Test**: It will fail because the feature doesn't exist
   ```bash
   uv run pytest tests/test_new_feature.py -v
   ```

3. **Implement the Feature**: Add the minimal code to make the test pass
   ```python
   @app.get("/new-feature")
   def new_feature():
       return {"feature": "implemented"}
   ```

4. **Run the Test Again**: It should pass now
   ```bash
   uv run pytest tests/test_new_feature.py -v
   ```

5. **Refactor**: Improve the implementation while ensuring the test still passes

## Testing Complex Routes

For routes that require database interaction, you have a few options:

1. **Mock the Database**: Create mock objects that simulate database behavior
2. **Use In-Memory Database**: Set up a SQLite in-memory database for tests
3. **Integration Tests**: Use a separate test database for full integration tests

## Mocking Dependencies

Here's how to mock dependencies in your tests:

```python
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_database():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = {"id": 1, "name": "Test"}
    return mock_db

def test_with_mock_db(mock_database):
    with patch('src.api.db.session.get_session', return_value=mock_database):
        # Your test code here
```

## References

- [Pytest with Eric's TDD Guide](https://pytest-with-eric.com/tdd/pytest-tdd/)
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html) 