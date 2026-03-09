# OMNI-AI Testing Guide

## Overview

This guide provides comprehensive information about testing the OMNI-AI system, including test structure, running tests, writing new tests, and understanding test coverage.

## Table of Contents

1. [Test Structure](#test-structure)
2. [Running Tests](#running-tests)
3. [Test Categories](#test-categories)
4. [Writing Tests](#writing-tests)
5. [Test Coverage](#test-coverage)
6. [CI/CD Integration](#cicd-integration)
7. [Best Practices](#best-practices)

---

## Test Structure

### Directory Layout

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── test_core_components.py        # Tests for NEXUS, Memory, AEGIS
├── test_specialized_agents.py     # Tests for all 9 specialized agents
├── test_integration.py            # Integration tests
├── test_performance.py            # Performance and scalability tests
└── fixtures/                      # Test fixtures and data
    ├── sample_data.json
    └── mock_responses.json

scripts/
└── run_tests.py                   # Test runner script
```

### Test File Organization

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **Performance Tests**: Test performance characteristics and scalability
- **End-to-End Tests**: Test complete workflows (future)

---

## Running Tests

### Using the Test Runner Script

The recommended way to run tests is using the test runner script:

```bash
# Run all tests
python scripts/run_tests.py

# Run with verbose output
python scripts/run_tests.py --verbose

# Run with coverage report
python scripts/run_tests.py --coverage

# Run unit tests only
python scripts/run_tests.py --unit

# Run integration tests only
python scripts/run_tests.py --integration

# Run performance tests only
python scripts/run_tests.py --performance

# Run specific test file
python scripts/run_tests.py --file tests/test_core_components.py

# Run tests matching pattern
python scripts/run_tests.py --pattern "memory"
```

### Using pytest Directly

You can also use pytest directly:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_core_components.py

# Run specific test
pytest tests/test_core_components.py::TestWorkingMemory::test_store_retrieve

# Run tests matching pattern
pytest -k "memory"

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only performance tests
pytest -m performance

# Skip slow tests
pytest -m "not slow"
```

### CI/CD Integration

For CI/CD pipelines:

```bash
# Run tests without output (for CI)
pytest -q --tb=no

# Generate coverage report for CI
pytest --cov=src --cov-report=xml --cov-report=term
```

---

## Test Categories

### Unit Tests

**Purpose**: Test individual components in isolation

**Files**:
- `test_core_components.py` - NEXUS, Memory, AEGIS
- `test_specialized_agents.py` - All 9 specialized agents

**Markers**: `@pytest.mark.unit`

**Example**:
```python
@pytest.mark.asyncio
async def test_working_memory_store():
    memory = WorkingMemory()
    await memory.store("key", {"data": "value"})
    result = await memory.retrieve("key")
    assert result == {"data": "value"}
```

### Integration Tests

**Purpose**: Test interactions between components

**Files**:
- `test_integration.py` - API integration, tool integration

**Markers**: `@pytest.mark.integration`

**Example**:
```python
@pytest.mark.asyncio
async def test_orchestrator_memory_integration():
    orchestrator = NEXUSOrchestrator()
    memory = WorkingMemory()
    
    await memory.store("task", {"data": "test"})
    result = await memory.retrieve("task")
    
    assert result is not None
```

### Performance Tests

**Purpose**: Test performance characteristics and scalability

**Files**:
- `test_performance.py` - Throughput, latency, scalability

**Markers**: `@pytest.mark.performance`

**Example**:
```python
@pytest.mark.asyncio
async def test_memory_throughput():
    memory = WorkingMemory()
    
    start = time.time()
    for i in range(1000):
        await memory.store(f"key_{i}", {"data": f"value_{i}"})
    
    duration = time.time() - start
    throughput = 1000 / duration
    
    assert throughput > 100  # At least 100 ops/sec
```

---

## Writing Tests

### Basic Test Structure

```python
import pytest
from src.module import ClassToTest

class TestClassName:
    """Test suite for ClassName."""
    
    @pytest.fixture
    def instance(self):
        """Create instance for testing."""
        return ClassToTest()
    
    @pytest.mark.asyncio
    async def test_method_name(self, instance):
        """Test a specific method."""
        # Arrange
        input_data = {"key": "value"}
        
        # Act
        result = await instance.method(input_data)
        
        # Assert
        assert result is not None
        assert result["status"] == "success"
```

### Async Tests

All async tests should use the `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_async_method(self):
    result = await some_async_function()
    assert result is not None
```

### Fixtures

Use fixtures to share setup code:

```python
@pytest.fixture
async def setup_data():
    """Setup test data."""
    data = {"key": "value"}
    yield data
    # Cleanup (if needed)

@pytest.mark.asyncio
async def test_with_fixture(self, setup_data):
    assert setup_data["key"] == "value"
```

### Mocking

Use mocking for external dependencies:

```python
from unittest.mock import Mock, AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock(self):
    # Create mock
    mock_agent = AsyncMock()
    mock_agent.process_task = AsyncMock(return_value={"result": "success"})
    
    # Use mock
    result = await orchestrator.distribute_task({"type": "test"})
    assert result is not None
    
    # Verify mock was called
    mock_agent.process_task.assert_called_once()
```

### Parametrized Tests

Run tests with multiple inputs:

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_multiplication(input, expected):
    assert multiply_by_two(input) == expected
```

---

## Test Coverage

### Current Coverage

As of this writing:

- **Core Components**: ~30%
- **Specialized Agents**: ~10%
- **Integration APIs**: ~5%
- **Advanced Tools**: ~0%

### Generating Coverage Reports

```bash
# Generate HTML report
pytest --cov=src --cov-report=html

# Generate terminal report
pytest --cov=src --cov-report=term-missing

# Generate both
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Viewing Coverage Reports

After generating HTML coverage:

```bash
# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Goals

- **Minimum Acceptable**: 70%
- **Target**: 80%
- **Ideal**: 90%+

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml --cov-report=term
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

---

## Best Practices

### 1. Test Independence

Each test should be independent and runnable in isolation:

```python
# ✅ Good
@pytest.mark.asyncio
async def test_1():
    await memory.store("key1", {"data": "value1"})

@pytest.mark.asyncio
async def test_2():
    await memory.store("key2", {"data": "value2"})

# ❌ Bad
@pytest.mark.asyncio
async def test_1():
    await memory.store("key", {"data": "value1"})

@pytest.mark.asyncio
async def test_2():
    # Depends on test_1
    result = await memory.retrieve("key")
```

### 2. Descriptive Test Names

Use clear, descriptive test names:

```python
# ✅ Good
async def test_working_memory_stores_and_retrieves_data_correctly():

# ❌ Bad
async def test_memory():
```

### 3. Arrange-Act-Assert Pattern

Structure tests clearly:

```python
@pytest.mark.asyncio
async def test_example(self, instance):
    # Arrange
    input_data = {"key": "value"}
    
    # Act
    result = await instance.process(input_data)
    
    # Assert
    assert result is not None
    assert result["status"] == "success"
```

### 4. Use Fixtures for Common Setup

Avoid code duplication:

```python
# ✅ Good
@pytest.fixture
def memory(self):
    return WorkingMemory()

@pytest.mark.asyncio
async def test_1(self, memory):
    await memory.store("key1", {"data": "value1"})

@pytest.mark.asyncio
async def test_2(self, memory):
    await memory.store("key2", {"data": "value2"})

# ❌ Bad
@pytest.mark.asyncio
async def test_1(self):
    memory = WorkingMemory()
    await memory.store("key1", {"data": "value1"})

@pytest.mark.asyncio
async def test_2(self):
    memory = WorkingMemory()  # Duplicated
    await memory.store("key2", {"data": "value2"})
```

### 5. Test Edge Cases

Don't just test happy paths:

```python
@pytest.mark.asyncio
async def test_normal_case(self, memory):
    await memory.store("key", {"data": "value"})
    assert await memory.retrieve("key") is not None

@pytest.mark.asyncio
async def test_empty_retrieval(self, memory):
    assert await memory.retrieve("nonexistent") is None

@pytest.mark.asyncio
async def test_expiry(self, memory):
    await memory.store("key", {"data": "value"}, ttl=1)
    assert await memory.retrieve("key") is not None
    await asyncio.sleep(1.5)
    assert await memory.retrieve("key") is None
```

### 6. Mock External Dependencies

Don't test external services:

```python
# ✅ Good
@patch('src.module.external_api_call')
async def test_with_mock(self, mock_api):
    mock_api.return_value = {"data": "mocked"}
    result = await process_data()
    assert result is not None

# ❌ Bad
async def test_without_mock(self):
    result = await external_api_call()  # Makes real API call
    assert result is not None
```

### 7. Keep Tests Fast

Optimize slow tests:

```python
# ✅ Good
@pytest.mark.asyncio
async def test_fast_operation(self):
    result = await fast_operation()
    assert result is not None

# ❌ Bad
@pytest.mark.asyncio
@pytest.mark.slow  # Mark as slow
async def test_slow_operation(self):
    result = await slow_operation_with_sleep()
    assert result is not None
```

### 8. Use Appropriate Assertions

Be specific with assertions:

```python
# ✅ Good
assert result["status"] == "success"
assert result["data"]["value"] == 42
assert len(result["items"]) == 5

# ❌ Bad
assert result is not None
assert "data" in result
```

### 9. Clean Up After Tests

Ensure tests don't leave state:

```python
@pytest.mark.asyncio
async def test_with_cleanup(self):
    # Setup
    await memory.store("key", {"data": "value"})
    
    # Test
    result = await memory.retrieve("key")
    assert result is not None
    
    # Cleanup
    await memory.clear()
```

### 10. Document Complex Tests

Add comments for complex test logic:

```python
@pytest.mark.asyncio
async def test_complex_scenario(self):
    """
    Test complex scenario with multiple steps:
    1. Store initial data
    2. Process with agent A
    3. Update data
    4. Process with agent B
    5. Verify final state
    """
    await memory.store("key", {"data": "initial"})
    # ... complex test logic ...
```

---

## Troubleshooting

### Common Issues

1. **Async Tests Not Running**
   - Ensure `@pytest.mark.asyncio` decorator is used
   - Check `pytest-asyncio` is installed

2. **Import Errors**
   - Ensure tests are run from project root
   - Check `PYTHONPATH` includes `src/`

3. **Fixture Not Found**
   - Ensure fixtures are in `conftest.py` or test class
   - Check fixture name is correct

4. **Slow Tests**
   - Use `@pytest.mark.slow` for slow tests
   - Skip slow tests with `-m "not slow"`

5. **Coverage Not Generated**
   - Ensure `pytest-cov` is installed
   - Check `--cov=src` flag is used

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-AsyncIO Documentation](https://pytest-asyncio.readthedocs.io/)
- [Pytest-Cov Documentation](https://pytest-cov.readthedocs.io/)

---

## Contributing Tests

When contributing new tests:

1. Follow the test structure and naming conventions
2. Use appropriate markers (unit, integration, performance)
3. Write descriptive docstrings for complex tests
4. Ensure tests are independent
5. Add fixtures for common setup
6. Mock external dependencies
7. Update this guide if adding new test patterns

---

**Last Updated**: 2025-01-18  
**Maintained By**: OMNI-AI Team