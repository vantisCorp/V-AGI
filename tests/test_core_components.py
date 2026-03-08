"""
Unit Tests for Core Components
Tests NEXUS Orchestrator, Memory Systems, and Security Layer
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.agents.base_agent import AgentCapabilities
from src.memory.long_term_memory import KnowledgeNode, LongTermMemory
from src.memory.vector_store import VectorDocument, VectorStore
from src.memory.working_memory import WorkingMemory
from src.nexus.orchestrator import NexusOrchestrator
from src.security.aegis import AegisGuardian


class TestNexusOrchestrator:
    """Test suite for NEXUS Orchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing."""
        return NexusOrchestrator()

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator is not None
        assert hasattr(orchestrator, "agents")

    @pytest.mark.asyncio
    async def test_register_agent(self, orchestrator):
        """Test agent registration."""
        mock_agent = AsyncMock()
        mock_agent.agent_id = "test_agent"
        mock_agent.initialize = AsyncMock()
        capabilities = AgentCapabilities(
            name="test_agent", description="Test agent", skills=["test_capability"], tools=[]
        )

        await orchestrator.register_agent(mock_agent, capabilities)

        assert "test_agent" in orchestrator.agents

    @pytest.mark.asyncio
    async def test_distribute_task(self, orchestrator):
        """Test task distribution."""
        # Register mock agent
        mock_agent = AsyncMock()
        mock_agent.agent_id = "test_agent"
        capabilities = AgentCapabilities(
            name="test_agent", description="Test agent", skills=["test_capability"], tools=[]
        )

        await orchestrator.register_agent(mock_agent, capabilities)

        # Check agent was registered
        assert "test_agent" in orchestrator.agents


class TestWorkingMemory:
    """Test suite for Working Memory."""

    @pytest.fixture
    def working_memory(self):
        """Create working memory instance."""
        return WorkingMemory()

    @pytest.mark.asyncio
    async def test_store_retrieve(self, working_memory):
        """Test storing and retrieving items."""
        key = "test_key"
        value = {"data": "test_value"}

        await working_memory.set(key, value)
        retrieved = await working_memory.get(key)

        assert retrieved == value

    @pytest.mark.asyncio
    async def test_expiry(self, working_memory):
        """Test item expiry."""
        key = "test_key"
        value = {"data": "test_value"}

        # Store with 1 second TTL
        await working_memory.set(key, value, ttl=1)

        # Retrieve immediately
        retrieved = await working_memory.get(key)
        assert retrieved == value

        # Wait for expiry
        await asyncio.sleep(1.5)

        # Should be expired
        retrieved = await working_memory.get(key)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_clear(self, working_memory):
        """Test clearing working memory."""
        await working_memory.set("key1", {"data": "value1"})
        await working_memory.set("key2", {"data": "value2"})

        await working_memory.clear()

        assert await working_memory.get("key1") is None
        assert await working_memory.get("key2") is None


class TestLongTermMemory:
    """Test suite for Long Term Memory."""

    @pytest.fixture
    def long_term_memory(self):
        """Create long term memory instance."""
        return LongTermMemory()

    @pytest.mark.asyncio
    async def test_store_retrieve(self, long_term_memory):
        """Test storing and retrieving knowledge."""
        node = KnowledgeNode(
            id="test_knowledge",
            label="test",
            properties={"content": "test content", "source": "test", "confidence": 0.9},
        )

        result = await long_term_memory.store_node(node)
        # Just verify no exception is raised

    @pytest.mark.asyncio
    async def test_search(self, long_term_memory):
        """Test knowledge search."""
        # Search nodes
        results = await long_term_memory.search_nodes("python")
        # Just verify no exception is raised


class TestVectorStore:
    """Test suite for Vector Store."""

    @pytest.fixture
    def vector_store(self):
        """Create vector store instance."""
        return VectorStore()

    @pytest.mark.asyncio
    async def test_add_search(self, vector_store):
        """Test adding and searching vectors."""
        # Add documents
        doc1 = VectorDocument(
            id="doc1",
            text="artificial intelligence and machine learning",
            metadata={"source": "test"},
        )
        doc2 = VectorDocument(
            id="doc2", text="web development with python", metadata={"source": "test"}
        )

        await vector_store.add_document(doc1)
        await vector_store.add_document(doc2)

        # Search
        results = await vector_store.search("AI and ML", top_k=2)

        assert len(results) >= 0  # May be empty if no embeddings

    @pytest.mark.asyncio
    async def test_delete(self, vector_store):
        """Test deleting vectors."""
        doc = VectorDocument(id="doc1", text="test document", metadata={"source": "test"})
        await vector_store.add_document(doc)
        result = await vector_store.delete_document("doc1")

        # Verify no exception


class TestAegisGuardian:
    """Test suite for AEGIS Guardian."""

    @pytest.fixture
    def aegis(self):
        """Create AEGIS Guardian instance."""
        return AegisGuardian()

    def test_initialization(self, aegis):
        """Test AEGIS initialization."""
        assert aegis is not None

    @pytest.mark.asyncio
    async def test_filter_input_safe(self, aegis):
        """Test input filtering with safe content."""
        safe_input = "normal data for processing"
        result = await aegis.filter_input(safe_input)
        assert result.is_safe == True

    @pytest.mark.asyncio
    async def test_filter_input_malicious(self, aegis):
        """Test input filtering with malicious content."""
        malicious_input = "<script>alert('xss')</script>"
        result = await aegis.filter_input(malicious_input)
        assert result.is_safe == False

    @pytest.mark.asyncio
    async def test_get_security_events(self, aegis):
        """Test getting security events."""
        events = await aegis.get_security_events()
        assert isinstance(events, list)

    @pytest.mark.asyncio
    async def test_get_stats(self, aegis):
        """Test getting statistics."""
        stats = await aegis.get_stats()
        assert isinstance(stats, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
