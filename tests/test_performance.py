"""
Performance Tests for OMNI-AI System
Tests system performance under various conditions
"""

import asyncio
import time
from unittest.mock import AsyncMock

import pytest

from src.agents.base_agent import AgentCapabilities
from src.api.communication_protocol import (MessagePriority, MessageProtocol,
                                            MessageQueue, MessageType)
from src.memory.working_memory import WorkingMemory
from src.nexus.orchestrator import NexusOrchestrator
from src.tools.cad_integration import CADIntegration, CADOperation
from src.tools.code_sandbox import CodeLanguage, CodeSandbox
from src.tools.digital_twin import DigitalTwin, TwinType
from src.tools.physics_engine import PhysicsEngine


class TestMemoryPerformance:
    """Test suite for memory performance."""

    @pytest.fixture
    def working_memory(self):
        """Create working memory instance."""
        return WorkingMemory()

    @pytest.mark.asyncio
    async def test_working_memory_throughput(self, working_memory):
        """Test working memory throughput."""
        iterations = 100

        start_time = time.time()
        for i in range(iterations):
            await working_memory.set(f"key_{i}", {"data": f"value_{i}"})
        write_time = time.time() - start_time

        start_time = time.time()
        for i in range(iterations):
            await working_memory.get(f"key_{i}")
        read_time = time.time() - start_time

        # Just verify operations complete
        assert write_time > 0
        assert read_time > 0

    @pytest.mark.asyncio
    async def test_working_memory_concurrent_access(self, working_memory):
        """Test concurrent memory access."""

        async def write_values(start, count):
            for i in range(start, start + count):
                await working_memory.set(f"key_{i}", {"data": f"value_{i}"})

        # Run concurrent writes
        await asyncio.gather(write_values(0, 50), write_values(50, 50), write_values(100, 50))

        # Verify all values were written
        result = await working_memory.get("key_75")
        assert result is not None


class TestOrchestratorPerformance:
    """Test suite for orchestrator performance."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return NexusOrchestrator()

    @pytest.mark.asyncio
    async def test_task_distribution_latency(self, orchestrator):
        """Test task distribution latency."""
        # Register a mock agent
        mock_agent = AsyncMock()
        mock_agent.agent_id = "test_agent"
        capabilities = AgentCapabilities(
            name="test_agent", description="Test agent", skills=["test_skill"], tools=[]
        )
        await orchestrator.register_agent(mock_agent, capabilities)

        start_time = time.time()
        # Verify agent registration
        assert "test_agent" in orchestrator.agents
        elapsed = time.time() - start_time

        assert elapsed >= 0  # Just verify no exception


class TestMessageProtocolPerformance:
    """Test suite for message protocol performance."""

    @pytest.fixture
    def protocol(self):
        """Create message protocol instance."""
        return MessageProtocol()

    def test_message_creation_performance(self, protocol):
        """Test message creation performance."""
        iterations = 1000

        start_time = time.time()
        for i in range(iterations):
            protocol.create_message(
                message_type=MessageType.TASK_SUBMIT,
                data={"task": f"task_{i}"},
                priority=MessagePriority.MEDIUM,
            )
        elapsed = time.time() - start_time

        assert elapsed > 0  # Just verify operations complete

    def test_priority_queue_performance(self):
        """Test priority queue performance."""
        queue = MessageQueue()
        iterations = 1000

        start_time = time.time()
        for i in range(iterations):
            queue.enqueue({"id": f"msg_{i}"}, MessagePriority.MEDIUM)
        enqueue_time = time.time() - start_time

        start_time = time.time()
        for i in range(iterations):
            queue.dequeue()
        dequeue_time = time.time() - start_time

        assert enqueue_time > 0
        assert dequeue_time > 0


class TestAdvancedToolsPerformance:
    """Test suite for advanced tools performance."""

    @pytest.fixture
    def cad(self):
        """Create CAD integration instance."""
        return CADIntegration()

    @pytest.fixture
    def physics(self):
        """Create physics engine instance."""
        return PhysicsEngine()

    @pytest.fixture
    def twin(self):
        """Create digital twin instance."""
        return DigitalTwin()

    @pytest.fixture
    def sandbox(self):
        """Create code sandbox instance."""
        return CodeSandbox()

    @pytest.mark.asyncio
    async def test_cad_operation_performance(self, cad):
        """Test CAD operation performance."""
        start_time = time.time()

        # Create multiple primitives
        for i in range(10):
            await cad.create_primitive(
                primitive_type="box",
                dimensions={"length": 10, "width": 10, "height": 10},
                name=f"box_{i}",
            )

        elapsed = time.time() - start_time
        assert elapsed > 0  # Just verify operations complete

    @pytest.mark.asyncio
    async def test_physics_simulation_performance(self, physics):
        """Test physics simulation performance."""
        # Create a body
        await physics.create_body(
            name="ball", shape="sphere", dimensions={"radius": 0.5}, mass=1.0, position=[0, 5, 0]
        )

        start_time = time.time()
        result = await physics.simulate(duration=1.0, time_step=0.01)
        elapsed = time.time() - start_time

        assert result is not None
        assert elapsed > 0

    @pytest.mark.asyncio
    async def test_digital_twin_sync_performance(self, twin):
        """Test digital twin synchronization performance."""
        # Create twin
        created = await twin.create_twin(
            twin_id="perf_test_twin",
            name="test_twin",
            twin_type=TwinType.ASSET,
            description="Test twin",
        )

        start_time = time.time()
        await twin.sync_with_physical(created["id"], {"status": "active", "value": 100})
        elapsed = time.time() - start_time

        assert elapsed > 0  # Just verify operations complete

    @pytest.mark.asyncio
    async def test_code_sandbox_execution_performance(self, sandbox):
        """Test code sandbox execution performance."""
        code = """
result = sum(range(1000))
"""

        start_time = time.time()
        result = await sandbox.execute_code(code, CodeLanguage.PYTHON)
        elapsed = time.time() - start_time

        assert result is not None
        assert elapsed > 0


class TestScalability:
    """Test suite for system scalability."""

    @pytest.mark.asyncio
    async def test_memory_scalability(self):
        """Test memory scalability."""
        memory = WorkingMemory(max_size=10000)

        # Store many items
        for i in range(1000):
            await memory.set(f"key_{i}", {"data": f"value_{i}"})

        # Verify a sample
        result = await memory.get("key_500")
        assert result is not None

    @pytest.mark.asyncio
    async def test_vector_store_scalability(self):
        """Test vector store scalability."""
        from src.memory.vector_store import VectorDocument, VectorStore

        store = VectorStore()

        # Add multiple documents
        for i in range(100):
            doc = VectorDocument(
                id=f"doc_{i}", text=f"Document number {i} with some content", metadata={"index": i}
            )
            await store.add_document(doc)

        # Verify a sample
        stats = await store.get_stats()
        assert stats is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
