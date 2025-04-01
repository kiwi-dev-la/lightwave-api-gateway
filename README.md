# Build an Analytics API using FastAPI + Time-series Postgres

Own your data pipeline! 

Start by building an Analytics API service with Python, FastAPI, and Time-series Postgres with TimescaleDB



## Docker

- `docker build -t analytics-api -f Dockerfile.web .`
- `docker run analytics-api `

becomes

- `docker compose up --watch`
- `docker compose down` or `docker compose down -v` (to remove volumes)
- `docker compose run app /bin/bash` or `docker compose run app python`

## Testing

This project follows Test-Driven Development (TDD) principles. Tests are written using pytest and organized by API endpoint.

### Running Tests

To run the tests:

```bash
# Install test dependencies and run tests
./run_tests.sh

# Run with coverage report
./run_tests.sh --cov=src

# Run specific tests
./run_tests.sh tests/test_events.py
```

### Test-Driven Development

Tests follow the Red-Green-Refactor cycle:

1. Write a failing test (Red)
2. Write minimal code to make the test pass (Green)
3. Refactor the code while keeping tests passing (Refactor)

For more details, see the [tests/README.md](tests/README.md) file.

## Development

For local development:

1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the API locally: `uvicorn src.main:app --reload` 