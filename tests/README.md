# Testing Suite

## Setup
```bash
pip install pytest pytest-cov
```

## Run Tests
```bash
pytest                    # All tests
pytest -v                 # Verbose
pytest --cov=app tests/   # With coverage
```

## Test Files
- `conftest.py` - Fixtures
- `test_auth.py` - Auth tests
- `test_services.py` - Service tests
- `test_routes.py` - Route tests
- `test_models.py` - Model tests
