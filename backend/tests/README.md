# Backend Unit Tests

This directory contains comprehensive unit tests for the licensing assistant backend.

## Test Structure

### Test Files

- **`conftest.py`** - Pytest configuration and shared fixtures
- **`test_ai_service.py`** - Tests for AI service functionality
- **`test_api_routes.py`** - Tests for API endpoints
- **`test_matching_service.py`** - Tests for regulatory matching logic
- **`test_helpers.py`** - Tests for API helper functions
- **`test_integration.py`** - Integration tests for complete workflows

### Test Categories

#### Unit Tests (`@pytest.mark.unit`)
- Test individual components in isolation
- Mock external dependencies
- Fast execution
- High coverage of business logic

#### Integration Tests (`@pytest.mark.integration`)
- Test complete workflows from API to response
- Test data flow through the system
- Test error handling across components

#### AI Tests (`@pytest.mark.ai`)
- Tests requiring AI service integration
- Mock OpenAI API responses
- Test AI prompt generation and response handling

## Running Tests

### Prerequisites

1. Install test dependencies:
   ```bash
   pip install pytest pytest-mock pytest-cov
   ```

2. Set up test environment:
   ```bash
   export FLASK_ENV=testing
   export OPENAI_API_KEY=test-key-for-testing
   ```

### Running All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### Running Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only AI tests
pytest -m ai
```

### Running Specific Test Files

```bash
# Test AI service only
pytest tests/test_ai_service.py

# Test API routes only
pytest tests/test_api_routes.py

# Test matching service only
pytest tests/test_matching_service.py
```

### Running Specific Test Functions

```bash
# Test specific function
pytest tests/test_ai_service.py::TestAIService::test_generate_smart_report_success

# Test specific class
pytest tests/test_api_routes.py::TestHealthEndpoints
```

## Test Configuration

### Environment Variables

Tests use the following environment variables:

- `FLASK_ENV=testing` - Flask testing mode
- `TESTING=True` - Enable test mode
- `OPENAI_API_KEY=test-key-for-testing` - Mock API key for AI tests
- `AI_MAX_TOKENS=1000` - AI configuration for tests
- `AI_TEMPERATURE=0.5` - AI configuration for tests

### Fixtures

Common fixtures available in all tests:

- **`app`** - Flask application instance
- **`client`** - Test client for making requests
- **`sample_business_data`** - Sample business data for testing
- **`sample_user_input`** - Sample user input for testing
- **`sample_questions`** - Sample questionnaire data
- **`mock_ai_response_success`** - Mock successful AI response
- **`mock_ai_response_failure`** - Mock failed AI response

## Test Coverage

### AI Service Tests (`test_ai_service.py`)

- ✅ AIResponse dataclass creation
- ✅ OpenAI strategy initialization
- ✅ Report generation success/failure
- ✅ Prompt generation for different report types
- ✅ Error handling and edge cases
- ✅ Provider availability checking

### API Routes Tests (`test_api_routes.py`)

- ✅ Health endpoints
- ✅ Questions endpoint
- ✅ Analyze endpoint (with/without AI)
- ✅ AI report generation endpoint
- ✅ AI providers endpoint
- ✅ Data validation
- ✅ Error handling
- ✅ Response structure validation

### Matching Service Tests (`test_matching_service.py`)

- ✅ User input normalization
- ✅ Numeric range extraction
- ✅ Requirements matching logic
- ✅ Business profile classification
- ✅ Relevance assessment
- ✅ Feature matching

### Helper Functions Tests (`test_helpers.py`)

- ✅ JSON loading functions
- ✅ Input validation
- ✅ Risk factor assessment
- ✅ Recommendations generation
- ✅ Questionnaire creation
- ✅ Feature options creation

### Integration Tests (`test_integration.py`)

- ✅ Complete workflow testing
- ✅ Data transformation flow
- ✅ Error handling across components
- ✅ AI provider integration
- ✅ Performance with large datasets

## Mocking Strategy

### External Dependencies

- **OpenAI API** - Mocked using `unittest.mock.patch`
- **File I/O** - Mocked using `unittest.mock.patch`
- **JSON loading** - Mocked for consistent test data

### Test Data

- Use realistic but minimal test data
- Cover edge cases and error conditions
- Ensure tests are deterministic and repeatable

## Best Practices

### Test Organization

1. **One test class per module/component**
2. **Descriptive test method names**
3. **Arrange-Act-Assert pattern**
4. **Clear test data setup**

### Test Isolation

1. **Each test is independent**
2. **No shared state between tests**
3. **Proper cleanup in fixtures**
4. **Mock external dependencies**

### Error Testing

1. **Test both success and failure paths**
2. **Test edge cases and boundary conditions**
3. **Test error handling and recovery**
4. **Verify error messages and status codes**

## Continuous Integration

### GitHub Actions

Tests should run on:
- Python 3.8+
- Different operating systems
- Pull request creation
- Main branch updates

### Test Reports

- Coverage reports generated automatically
- Test results published as artifacts
- Performance metrics tracked

## Troubleshooting

### Common Issues

1. **Import errors** - Check Python path and dependencies
2. **Mock failures** - Verify mock setup and call assertions
3. **Test data issues** - Ensure test data is valid and complete
4. **Environment issues** - Check environment variables and Flask config

### Debug Mode

Run tests in debug mode:

```bash
# Run with debug output
pytest -v -s

# Run single test with debug
pytest -v -s tests/test_ai_service.py::TestAIService::test_generate_smart_report_success
```

### Test Data Issues

If tests fail due to data issues:

1. Check fixture data in `conftest.py`
2. Verify mock data matches expected structure
3. Ensure test data covers all required fields
4. Check for data type mismatches
