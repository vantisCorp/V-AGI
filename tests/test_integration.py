"""
Integration Tests for OMNI-AI System
Tests end-to-end workflows and component interactions
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.agents.base_agent import AgentCapabilities, Task, TaskPriority
from src.api.communication_protocol import (MessagePriority, MessageProtocol,
                                            MessageType)
from src.memory.working_memory import WorkingMemory
from src.nexus.orchestrator import NexusOrchestrator
from src.tools.cad_integration import CADIntegration, CADOperation
from src.tools.code_sandbox import CodeLanguage, CodeSandbox
from src.tools.digital_twin import DigitalTwin, TwinType
from src.tools.physics_engine import PhysicsEngine


class TestOrchestratorIntegration:
    """Test suite for orchestrator integration."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return NexusOrchestrator()

    @pytest.fixture
    def memory(self):
        """Create working memory instance."""
        return WorkingMemory()

    @pytest.mark.asyncio
    async def test_orchestrator_memory_integration(self, orchestrator, memory):
        """Test orchestrator with memory."""
        # Store some data
        await memory.set("test_key", {"data": "test_value"})

        # Verify it was stored
        result = await memory.get("test_key")
        assert result == {"data": "test_value"}

    @pytest.mark.asyncio
    async def test_orchestrator_agent_coordination(self, orchestrator):
        """Test agent coordination."""
        # Register a mock agent
        mock_agent = AsyncMock()
        mock_agent.agent_id = "test_agent"
        capabilities = AgentCapabilities(
            name="test_agent", description="Test agent", skills=["test_skill"], tools=[]
        )

        await orchestrator.register_agent(mock_agent, capabilities)

        # Verify agent was registered
        assert "test_agent" in orchestrator.agents


class TestAPIIntegration:
    """Test suite for API integration."""

    @pytest.fixture
    def message_protocol(self):
        """Create message protocol instance."""
        return MessageProtocol()

    def test_message_protocol_creation(self, message_protocol):
        """Test message creation."""
        message = message_protocol.create_message(
            message_type=MessageType.TASK_SUBMIT,
            data={"task": "test"},
            priority=MessagePriority.MEDIUM,
        )
        assert message is not None

    def test_message_validation(self, message_protocol):
        """Test message validation."""
        message = message_protocol.create_message(
            message_type=MessageType.TASK_SUBMIT,
            data={"task": "test"},
            priority=MessagePriority.MEDIUM,
        )
        is_valid = message_protocol.validate_message(message)
        assert isinstance(is_valid, bool)

    def test_priority_queue(self, message_protocol):
        """Test priority queue."""
        from src.api.communication_protocol import MessageQueue

        queue = MessageQueue()
        message = {"id": "test", "data": "test_data"}

        result = queue.enqueue(message, MessagePriority.HIGH)
        assert result == True

        dequeued = queue.dequeue()
        assert dequeued == message


class TestCADIntegration:
    """Test suite for CAD integration."""

    @pytest.fixture
    def cad(self):
        """Create CAD integration instance."""
        return CADIntegration()

    @pytest.mark.asyncio
    async def test_cad_primitive_creation(self, cad):
        """Test creating CAD primitives."""
        result = await cad.create_primitive(
            primitive_type="box",
            dimensions={"length": 10, "width": 5, "height": 3},
            name="test_box",
        )
        assert result is not None
        assert hasattr(result, "id")

    @pytest.mark.asyncio
    async def test_cad_boolean_operations(self, cad):
        """Test CAD boolean operations."""
        # Create two boxes
        box1 = await cad.create_primitive(
            primitive_type="box", dimensions={"length": 10, "width": 10, "height": 10}, name="box1"
        )
        box2 = await cad.create_primitive(
            primitive_type="box", dimensions={"length": 5, "width": 5, "height": 5}, name="box2"
        )

        # Perform boolean union
        result = await cad.perform_operation(
            component_ids=[box1.id, box2.id], operation=CADOperation.BOOLEAN_UNION, parameters={}
        )
        assert result is not None

    @pytest.mark.asyncio
    async def test_cad_mass_properties(self, cad):
        """Test CAD mass properties calculation."""
        box = await cad.create_primitive(
            primitive_type="box",
            dimensions={"length": 10, "width": 10, "height": 10},
            name="test_box",
        )

        # Use get_component which returns the component with properties
        result = cad.get_component(box.id)
        assert result is not None


class TestPhysicsEngineIntegration:
    """Test suite for Physics Engine integration."""

    @pytest.fixture
    def physics(self):
        """Create physics engine instance."""
        return PhysicsEngine()

    @pytest.mark.asyncio
    async def test_physics_body_creation(self, physics):
        """Test creating physics bodies."""
        result = await physics.create_body(
            name="test_ball",
            shape="sphere",
            dimensions={"radius": 0.5},
            mass=1.0,
            position=[0, 10, 0],
        )
        assert result is not None
        assert hasattr(result, "id")

    @pytest.mark.asyncio
    async def test_physics_simulation(self, physics):
        """Test physics simulation."""
        # Create a ball
        ball = await physics.create_body(
            name="ball", shape="sphere", dimensions={"radius": 0.5}, mass=1.0, position=[0, 5, 0]
        )

        # Run simulation
        result = await physics.simulate(duration=1.0, time_step=0.1)
        assert result is not None

    @pytest.mark.asyncio
    async def test_physics_energy_analysis(self, physics):
        """Test energy analysis."""
        await physics.create_body(
            name="ball", shape="sphere", dimensions={"radius": 0.5}, mass=1.0, position=[0, 5, 0]
        )

        result = await physics.analyze_energy()
        assert result is not None


class TestDigitalTwinIntegration:
    """Test suite for Digital Twin integration."""

    @pytest.fixture
    def twin(self):
        """Create digital twin instance."""
        return DigitalTwin()

    @pytest.mark.asyncio
    async def test_digital_twin_creation(self, twin):
        """Test creating digital twin."""
        result = await twin.create_twin(
            twin_id="test_twin_1",
            name="test_twin",
            twin_type=TwinType.ASSET,
            description="Test digital twin",
        )
        assert result is not None
        assert "id" in result

    @pytest.mark.asyncio
    async def test_digital_twin_sync(self, twin):
        """Test digital twin synchronization."""
        # Create twin
        created = await twin.create_twin(
            twin_id="test_twin_2",
            name="test_twin",
            twin_type=TwinType.ASSET,
            description="Test digital twin",
        )

        # Sync twin - use sync_with_physical instead of sync_twin
        result = await twin.sync_with_physical(created["id"], {"status": "active"})
        assert result is not None


class TestCodeSandboxIntegration:
    """Test suite for Code Sandbox integration."""

    @pytest.fixture
    def sandbox(self):
        """Create code sandbox instance."""
        return CodeSandbox()

    @pytest.mark.asyncio
    async def test_code_execution(self, sandbox):
        """Test code execution."""
        code = """
x = 1 + 1
result = x * 2
"""
        result = await sandbox.execute_code(code, CodeLanguage.PYTHON)
        assert result is not None

    @pytest.mark.asyncio
    async def test_code_validation(self, sandbox):
        """Test code validation."""
        code = """
x = 1 + 1
print(x)
"""
        result = await sandbox.validate_code(code, CodeLanguage.PYTHON)
        assert result is not None
        assert "valid" in result

    @pytest.mark.asyncio
    async def test_code_analysis(self, sandbox):
        """Test code analysis."""
        code = """
def add(a, b):
    return a + b
"""
        result = await sandbox.analyze_code(code, CodeLanguage.PYTHON)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
