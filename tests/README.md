# Tests Directory

This directory contains all test files for the LDAP Employee Directory application.

## Test Structure

```
tests/
├── conftest.py                          # Pytest configuration and fixtures
├── unit/                                # Unit tests
│   ├── test_ldap_service.py            # LDAP service layer tests
│   ├── test_auth.py                    # Authentication module tests
│   └── test_app.py                     # Flask application tests
├── security/                            # Security tests
│   ├── test_security_ldap_injection.py # LDAP injection protection tests
│   ├── test_security_auth.py           # Authentication security tests
│   └── test_security_validation.py     # Input validation tests
└── integration/                         # Integration tests
    └── test_integration_flows.py        # End-to-end flow tests
```

## Running Tests

### All Tests
```bash
pytest
```

### With Coverage
```bash
pytest --cov=. --cov-report=html --cov-report=term
```

### Specific Test Categories
```bash
pytest tests/unit/
pytest tests/security/
pytest tests/integration/
```

### Specific Test File
```bash
pytest tests/unit/test_ldap_service.py -v
```

### With Verbose Output
```bash
pytest -v
```

## Test Coverage Goals

- **Unit Tests**: 85%+ code coverage
- **Security Tests**: 100% coverage of input points
- **Integration Tests**: 70%+ coverage of user flows

## Writing New Tests

When adding new tests:

1. Place unit tests in `tests/unit/`
2. Place security tests in `tests/security/`
3. Place integration tests in `tests/integration/`
4. Use descriptive test names: `test_<functionality>_<scenario>`
5. Add docstrings to explain what is being tested
6. Use fixtures for common setup
7. Mock external dependencies (LDAP, Redis, etc.)

## Test Dependencies

All test dependencies are included in `requirements.txt`:

- pytest
- pytest-cov
- pytest-mock
- pytest-flask
