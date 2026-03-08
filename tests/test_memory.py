"""
Tests for Memory Modules (Long-Term Memory, Working Memory, Vector Store).
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.memory.long_term_memory import (NEO4J_AVAILABLE, KnowledgeNode,
                                         KnowledgeRelationship, LongTermMemory)
from src.memory.vector_store import VectorDocument, VectorStore
from src.memory.working_memory import MemoryItem, WorkingMemory


class TestKnowledgeNode:
    """Test suite for KnowledgeNode dataclass."""

    def test_knowledge_node_creation(self):
        """Test creating a knowledge node."""
        node = KnowledgeNode(
            id="test-node-1", label="Concept", properties={"name": "Test", "value": 42}
        )
        assert node.id == "test-node-1"
        assert node.label == "Concept"
        assert node.properties["name"] == "Test"

    def test_knowledge_node_to_dict(self):
        """Test converting node to dictionary."""
        node = KnowledgeNode(id="test-node-2", label="Entity", properties={"key": "value"})
        result = node.to_dict()
        assert result["id"] == "test-node-2"
        assert result["label"] == "Entity"


class TestKnowledgeRelationship:
    """Test suite for KnowledgeRelationship dataclass."""

    def test_relationship_creation(self):
        """Test creating a knowledge relationship."""
        rel = KnowledgeRelationship(
            source="node-1",
            target="node-2",
            relationship_type="RELATES_TO",
            properties={"weight": 0.8},
        )
        assert rel.source == "node-1"
        assert rel.target == "node-2"
        assert rel.relationship_type == "RELATES_TO"

    def test_relationship_to_dict(self):
        """Test converting relationship to dictionary."""
        rel = KnowledgeRelationship(source="node-a", target="node-b", relationship_type="CONNECTS")
        result = rel.to_dict()
        assert result["source"] == "node-a"
        assert result["target"] == "node-b"


class TestLongTermMemory:
    """Test suite for LongTermMemory class."""

    @pytest.fixture
    def ltm_disabled(self):
        """Create LongTermMemory with disabled Neo4j."""
        return LongTermMemory(enabled=False)

    def test_init_disabled(self, ltm_disabled):
        """Test initialization with disabled flag."""
        assert ltm_disabled.enabled is False
        assert ltm_disabled.driver is None

    @pytest.mark.asyncio
    async def test_store_node_disabled(self, ltm_disabled):
        """Test storing node when disabled."""
        node = KnowledgeNode(id="test", label="Test")
        result = await ltm_disabled.store_node(node)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_node_disabled(self, ltm_disabled):
        """Test getting node when disabled."""
        result = await ltm_disabled.get_node("test-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_create_relationship_disabled(self, ltm_disabled):
        """Test creating relationship when disabled."""
        result = await ltm_disabled.create_relationship("node-1", "node-2", "RELATES_TO")
        assert result is False

    @pytest.mark.asyncio
    async def test_search_nodes_disabled(self, ltm_disabled):
        """Test searching nodes when disabled."""
        result = await ltm_disabled.search_nodes("query")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_connected_nodes_disabled(self, ltm_disabled):
        """Test getting connected nodes when disabled."""
        result = await ltm_disabled.get_connected_nodes("node-id")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_stats_disabled(self, ltm_disabled):
        """Test getting stats when disabled."""
        result = await ltm_disabled.get_stats()
        assert "enabled" in result


class TestMemoryItem:
    """Test suite for MemoryItem dataclass."""

    def test_memory_item_creation(self):
        """Test creating a memory item."""
        item = MemoryItem(key="mem-1", value="Test content", ttl=60)
        assert item.key == "mem-1"
        assert item.value == "Test content"


class TestWorkingMemory:
    """Test suite for WorkingMemory class."""

    @pytest.fixture
    def working_memory(self):
        """Create WorkingMemory instance."""
        return WorkingMemory(max_size=100)

    def test_init(self, working_memory):
        """Test initialization."""
        assert working_memory.max_size == 100

    @pytest.mark.asyncio
    async def test_set_and_get(self, working_memory):
        """Test setting and getting an item."""
        await working_memory.set("test-id", "Test content")
        result = await working_memory.get("test-id")
        assert result == "Test content"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, working_memory):
        """Test getting non-existent item."""
        result = await working_memory.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_item(self, working_memory):
        """Test deleting an item."""
        await working_memory.set("test-id", "Test content")
        result = await working_memory.delete("test-id")
        assert result is True

    @pytest.mark.asyncio
    async def test_clear(self, working_memory):
        """Test clearing all items."""
        await working_memory.set("id-1", "Content 1")
        await working_memory.set("id-2", "Content 2")
        await working_memory.clear()
        size = await working_memory.get_size()
        assert size == 0

    @pytest.mark.asyncio
    async def test_get_keys(self, working_memory):
        """Test getting all keys."""
        await working_memory.set("id-1", "Content 1")
        await working_memory.set("id-2", "Content 2")
        keys = await working_memory.get_keys()
        assert len(keys) == 2

    @pytest.mark.asyncio
    async def test_get_stats(self, working_memory):
        """Test getting stats."""
        await working_memory.set("id-1", "Content 1")
        stats = await working_memory.get_stats()
        assert stats["size"] == 1


class TestVectorDocument:
    """Test suite for VectorDocument dataclass."""

    def test_vector_document_creation(self):
        """Test creating a vector document."""
        doc = VectorDocument(id="doc-1", text="Test content", metadata={"source": "test"})
        assert doc.id == "doc-1"
        assert doc.text == "Test content"

    def test_vector_document_to_dict(self):
        """Test converting vector document to dictionary."""
        doc = VectorDocument(id="doc-2", text="Content", metadata={"key": "value"})
        result = doc.to_dict()
        assert result["id"] == "doc-2"
        assert result["text"] == "Content"


class TestVectorStore:
    """Test suite for VectorStore class."""

    @pytest.fixture
    def vector_store(self):
        """Create VectorStore instance."""
        return VectorStore(dimension=128, enabled=False)

    def test_init(self, vector_store):
        """Test initialization."""
        assert vector_store.dimension == 128

    @pytest.mark.asyncio
    async def test_add_document_disabled(self, vector_store):
        """Test adding a document when disabled."""
        doc = VectorDocument(id="doc-1", text="Test content")
        result = await vector_store.add_document(doc)
        assert result is False

    @pytest.mark.asyncio
    async def test_search_disabled(self, vector_store):
        """Test searching when disabled."""
        results = await vector_store.search("AI", top_k=5)
        assert results == []

    @pytest.mark.asyncio
    async def test_delete_document_disabled(self, vector_store):
        """Test deleting a document when disabled."""
        result = await vector_store.delete_document("doc-1")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_stats_disabled(self, vector_store):
        """Test getting stats when disabled."""
        stats = await vector_store.get_stats()
        assert "enabled" in stats
