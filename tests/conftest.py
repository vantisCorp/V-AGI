"""
Pytest configuration for OMNI-AI tests
"""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_task():
    """Provide a sample task for testing."""
    from src.agents.base_agent import Task, TaskPriority
    return Task(
        id="test_task_001",
        description="Sample test task",
        parameters={"test_param": "test_value"},
        priority=TaskPriority.MEDIUM
    )


@pytest.fixture
def sample_capabilities():
    """Provide sample agent capabilities for testing."""
    from src.agents.base_agent import AgentCapabilities
    return AgentCapabilities(
        name="TestAgent",
        description="Test agent for unit tests",
        skills=["skill1", "skill2"],
        tools=["tool1", "tool2"],
        max_concurrent_tasks=1,
        specialization="test"
    )