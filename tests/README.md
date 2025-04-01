# Test-Driven Development for Analytics API

This test suite follows the Test-Driven Development (TDD) principles as described in [Pytest with Eric's TDD guide](https://pytest-with-eric.com/tdd/pytest-tdd/).

## TDD Process (Red-Green-Refactor)

The tests in this project follow these TDD steps:

1. **Write the Test (Red)**: First, write a test for a feature before implementing the feature itself.
2. **Write the Minimum Code (Green)**: Next, write just enough code to make the test pass.
3. **Run The Test (Green)**: Verify the code passes the test.
4. **Refactor/Improve Code (Refactor)**: Clean up the code while ensuring tests still pass.
5. **Repeat**: Continue with the next feature or enhancement.

## Test Structure

Tests are organized by API endpoint:

- `test_health.py`: Tests for the `/healthz` endpoint
- `test_root.py`: Tests for the `/` endpoint
- `test_items.py`: Tests for the `/items/{item_id}` endpoint
- `test_events.py`: Tests for the `/api/events` endpoints

## Running Tests

To run the tests:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests for a specific file
pytest tests/test_events.py

# Run a specific test
pytest tests/test_events.py::test_create_event
```

## Test Database

Tests use an in-memory SQLite database with the TimescaleDB extension to avoid affecting the production database. The test database is set up and torn down for each test function.

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `test_client`: Creates a FastAPI TestClient for making HTTP requests
- `test_db`: Sets up an in-memory test database and provides a session 