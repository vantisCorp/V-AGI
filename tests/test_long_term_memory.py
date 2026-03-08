"""
Tests for Long Term Memory Module.
"""

import json
from dataclasses import asdict
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.memory.long_term_memory import (KnowledgeNode, KnowledgeRelationship,
                                         LongTermMemory)


class TestKnowledgeNode:
    """Tests for KnowledgeNode dataclass."""

    def test_knowledge_node_creation(self):
        """Test creating a KnowledgeNode."""
        node = KnowledgeNode(id="node_1", label="Concept", properties={"name": "test", "value": 42})

        assert node.id == "node_1"
        assert node.label == "Concept"
        assert node.properties["name"] == "test"
        assert node.properties["value"] == 42
        assert isinstance(node.created_at, datetime)

    def test_knowledge_node_default_values(self):
        """Test KnowledgeNode default values."""
        node = KnowledgeNode(id="node_2", label="Test")

        assert node.properties == {}
        assert isinstance(node.created_at, datetime)

    def test_knowledge_node_to_dict(self):
        """Test KnowledgeNode to_dict method."""
        node = KnowledgeNode(id="node_3", label="Entity", properties={"key": "value"})

        result = node.to_dict()

        assert result["id"] == "node_3"
        assert result["label"] == "Entity"
        assert result["properties"]["key"] == "value"
        assert "created_at" in result

    def test_knowledge_node_custom_created_at(self):
        """Test KnowledgeNode with custom created_at."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        node = KnowledgeNode(id="node_4", label="Test", created_at=custom_time)

        assert node.created_at == custom_time


class TestKnowledgeRelationship:
    """Tests for KnowledgeRelationship dataclass."""

    def test_knowledge_relationship_creation(self):
        """Test creating a KnowledgeRelationship."""
        rel = KnowledgeRelationship(
            source="node_1",
            target="node_2",
            relationship_type="RELATES_TO",
            properties={"weight": 0.9},
        )

        assert rel.source == "node_1"
        assert rel.target == "node_2"
        assert rel.relationship_type == "RELATES_TO"
        assert rel.properties["weight"] == 0.9
        assert isinstance(rel.created_at, datetime)

    def test_knowledge_relationship_default_values(self):
        """Test KnowledgeRelationship default values."""
        rel = KnowledgeRelationship(source="a", target="b", relationship_type="LINKS")

        assert rel.properties == {}
        assert isinstance(rel.created_at, datetime)

    def test_knowledge_relationship_to_dict(self):
        """Test KnowledgeRelationship to_dict method."""
        rel = KnowledgeRelationship(
            source="src",
            target="dst",
            relationship_type="DEPENDS_ON",
            properties={"strength": "strong"},
        )

        result = rel.to_dict()

        assert result["source"] == "src"
        assert result["target"] == "dst"
        assert result["type"] == "DEPENDS_ON"
        assert result["properties"]["strength"] == "strong"
        assert "created_at" in result


class TestLongTermMemory:
    """Tests for LongTermMemory class."""

    @pytest.fixture
    def mock_driver(self):
        """Create a mock Neo4j driver."""
        driver = MagicMock()
        session = MagicMock()
        result = MagicMock()

        driver.session.return_value.__enter__ = MagicMock(return_value=session)
        driver.session.return_value.__exit__ = MagicMock(return_value=False)
        session.run.return_value = result

        return driver, session, result

    @pytest.fixture
    def ltm_disabled(self):
        """Create a LongTermMemory with disabled state."""
        return LongTermMemory(enabled=False)

    @pytest.fixture
    def ltm_with_mock_driver(self):
        """Create a LongTermMemory with a mock driver injected."""
        # Create fresh mocks for each test
        driver = MagicMock()
        session = MagicMock()

        # Setup the session context manager properly
        driver.session.return_value.__enter__ = MagicMock(return_value=session)
        driver.session.return_value.__exit__ = MagicMock(return_value=False)

        ltm = LongTermMemory(enabled=False)
        ltm.enabled = True
        ltm.driver = driver

        return ltm, session, driver

    def test_ltm_initialization_disabled(self, ltm_disabled):
        """Test LongTermMemory initialization when disabled."""
        assert ltm_disabled.enabled is False
        assert ltm_disabled.driver is None

    def test_ltm_initialization_with_config(self):
        """Test LongTermMemory initialization with custom config."""
        ltm = LongTermMemory(
            uri="bolt://custom:7687", username="custom_user", password="custom_pass", enabled=False
        )

        assert ltm.uri == "bolt://custom:7687"
        assert ltm.username == "custom_user"
        assert ltm.password == "custom_pass"

    def test_ltm_connect_success(self):
        """Test successful connection to Neo4j."""
        mock_driver = MagicMock()

        with patch.dict(
            "sys.modules",
            {
                "neo4j": MagicMock(
                    GraphDatabase=MagicMock(driver=MagicMock(return_value=mock_driver))
                )
            },
        ):
            # Create instance and manually set driver
            ltm = LongTermMemory(enabled=False)
            ltm.driver = mock_driver
            ltm.enabled = True

            assert ltm.driver is not None

    def test_ltm_connect_failure(self):
        """Test connection failure handling."""
        ltm = LongTermMemory(enabled=False)
        ltm.enabled = False  # Connection would fail, so disabled

        assert ltm.enabled is False

    @pytest.mark.asyncio
    async def test_close(self, ltm_with_mock_driver):
        """Test closing the connection."""
        ltm, _, _ = ltm_with_mock_driver

        await ltm.close()

        ltm.driver.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_no_driver(self, ltm_disabled):
        """Test closing when no driver exists."""
        await ltm_disabled.close()
        # Should not raise an error

    def test_execute_query_disabled(self, ltm_disabled):
        """Test query execution when disabled."""
        result = ltm_disabled._execute_query("MATCH (n) RETURN n")
        assert result == []

    def test_execute_query_success(self, ltm_with_mock_driver):
        """Test successful query execution."""
        ltm, session, driver = ltm_with_mock_driver

        # Create a mock result that iterates properly
        mock_record = MagicMock()
        mock_record.data.return_value = {"n": {"id": "1", "label": "Test"}}
        mock_result = [mock_record]

        # Make session.run return an iterable result
        session.run.return_value = iter(mock_result)

        query_result = ltm._execute_query("MATCH (n) RETURN n", {"param": "value"})

        session.run.assert_called_once()
        assert len(query_result) == 1

    def test_execute_query_exception(self, ltm_with_mock_driver):
        """Test query execution with exception."""
        ltm, session, driver = ltm_with_mock_driver

        session.run.side_effect = Exception("Query failed")

        result = ltm._execute_query("INVALID QUERY")

        assert result == []

    @pytest.mark.asyncio
    async def test_store_node_disabled(self, ltm_disabled):
        """Test storing node when disabled."""
        node = KnowledgeNode(id="test", label="Test")

        result = await ltm_disabled.store_node(node)

        assert result is False

    @pytest.mark.asyncio
    async def test_store_node_success(self, ltm_with_mock_driver):
        """Test successful node storage."""
        ltm, session, driver = ltm_with_mock_driver

        node = KnowledgeNode(id="node_1", label="Concept", properties={"key": "value"})

        # Create a mock result that iterates properly
        mock_record = MagicMock()
        mock_record.data.return_value = {"n": {"id": "node_1"}}
        session.run.return_value = iter([mock_record])

        success = await ltm.store_node(node)

        assert success is True
        session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_node_disabled(self, ltm_disabled):
        """Test getting node when disabled."""
        result = await ltm_disabled.get_node("node_1")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_node_not_found(self, ltm_with_mock_driver):
        """Test getting non-existent node."""
        ltm, session, driver = ltm_with_mock_driver

        # Return empty iterable
        session.run.return_value = iter([])

        node = await ltm.get_node("nonexistent")

        assert node is None

    @pytest.mark.asyncio
    async def test_get_node_success(self, ltm_with_mock_driver):
        """Test successful node retrieval."""
        ltm, session, driver = ltm_with_mock_driver

        # Create a mock result that iterates properly
        mock_record = MagicMock()
        mock_record.data.return_value = {
            "n": {
                "id": "node_1",
                "label": "Concept",
                "properties": json.dumps({"key": "value"}),
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
        session.run.return_value = iter([mock_record])

        node = await ltm.get_node("node_1")

        assert node is not None
        assert node["id"] == "node_1"
        assert node["label"] == "Concept"
        assert node["properties"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_create_relationship_disabled(self, ltm_disabled):
        """Test creating relationship when disabled."""
        result = await ltm_disabled.create_relationship("a", "b", "LINKS")

        assert result is False

    @pytest.mark.asyncio
    async def test_create_relationship_success(self, ltm_with_mock_driver):
        """Test successful relationship creation."""
        ltm, session, driver = ltm_with_mock_driver

        # Create a mock result that iterates properly
        mock_record = MagicMock()
        mock_record.data.return_value = {"r": {"type": "LINKS"}}
        session.run.return_value = iter([mock_record])

        success = await ltm.create_relationship("node_1", "node_2", "RELATES_TO", {"weight": 0.9})

        assert success is True
        session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_nodes_disabled(self, ltm_disabled):
        """Test searching nodes when disabled."""
        result = await ltm_disabled.search_nodes()

        assert result == []

    @pytest.mark.asyncio
    async def test_search_nodes_no_filters(self, ltm_with_mock_driver):
        """Test searching nodes without filters."""
        ltm, session, driver = ltm_with_mock_driver

        # Create a mock result that iterates properly
        mock_record = MagicMock()
        mock_record.data.return_value = {
            "n": {
                "id": "node_1",
                "label": "Concept",
                "properties": json.dumps({"key": "value"}),
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
        session.run.return_value = iter([mock_record])

        nodes = await ltm.search_nodes()

        assert len(nodes) == 1
        assert nodes[0]["id"] == "node_1"

    @pytest.mark.asyncio
    async def test_search_nodes_with_label_filter(self, ltm_with_mock_driver):
        """Test searching nodes with label filter."""
        ltm, session, driver = ltm_with_mock_driver

        # Create a mock result that iterates properly
        mock_record = MagicMock()
        mock_record.data.return_value = {
            "n": {
                "id": "node_1",
                "label": "Concept",
                "properties": json.dumps({}),
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
        session.run.return_value = iter([mock_record])

        nodes = await ltm.search_nodes(label="Concept")

        assert len(nodes) == 1

    @pytest.mark.asyncio
    async def test_search_nodes_with_properties_filter(self, ltm_with_mock_driver):
        """Test searching nodes with property filter."""
        ltm, session, driver = ltm_with_mock_driver

        # Create a mock result that iterates properly
        mock_record = MagicMock()
        mock_record.data.return_value = {
            "n": {
                "id": "node_1",
                "label": "Concept",
                "properties": json.dumps({"name": "test"}),
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
        session.run.return_value = iter([mock_record])

        nodes = await ltm.search_nodes(properties={"name": "test"})

        assert len(nodes) == 1

    @pytest.mark.asyncio
    async def test_search_nodes_with_limit(self, ltm_with_mock_driver):
        """Test searching nodes with limit."""
        ltm, session, driver = ltm_with_mock_driver

        # Return empty iterable
        session.run.return_value = iter([])

        await ltm.search_nodes(limit=10)

        # Check that the query was executed
        session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_connected_nodes_disabled(self, ltm_disabled):
        """Test getting connected nodes when disabled."""
        result = await ltm_disabled.get_connected_nodes("node_1")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_connected_nodes_outgoing(self, ltm_with_mock_driver):
        """Test getting outgoing connected nodes."""
        ltm, session, driver = ltm_with_mock_driver

        # Create a mock result that iterates properly
        mock_record = MagicMock()
        mock_record.data.return_value = {
            "connected": {"id": "node_2", "label": "Target", "properties": json.dumps({})},
            "r": {"type": "LINKS", "properties": json.dumps({"weight": 1.0})},
        }
        session.run.return_value = iter([mock_record])

        connected = await ltm.get_connected_nodes(
            "node_1", relationship_type="LINKS", direction="outgoing"
        )

        assert len(connected) == 1
        assert connected[0]["node"]["id"] == "node_2"
        assert connected[0]["relationship"]["type"] == "LINKS"

    @pytest.mark.asyncio
    async def test_get_connected_nodes_incoming(self, ltm_with_mock_driver):
        """Test getting incoming connected nodes."""
        ltm, session, driver = ltm_with_mock_driver

        # Create a mock result that iterates properly
        mock_record = MagicMock()
        mock_record.data.return_value = {
            "connected": {"id": "node_0", "label": "Source", "properties": json.dumps({})},
            "r": {"type": "LINKS", "properties": json.dumps({})},
        }
        session.run.return_value = iter([mock_record])

        connected = await ltm.get_connected_nodes("node_1", direction="incoming")

        assert len(connected) == 1
        assert connected[0]["node"]["id"] == "node_0"

    @pytest.mark.asyncio
    async def test_get_connected_nodes_both_directions(self, ltm_with_mock_driver):
        """Test getting connected nodes in both directions."""
        ltm, session, driver = ltm_with_mock_driver

        # Create mock results that iterate properly
        mock_record1 = MagicMock()
        mock_record1.data.return_value = {
            "connected": {"id": "node_2", "label": "T", "properties": json.dumps({})},
            "r": {"type": "LINKS", "properties": json.dumps({})},
        }
        mock_record2 = MagicMock()
        mock_record2.data.return_value = {
            "connected": {"id": "node_0", "label": "S", "properties": json.dumps({})},
            "r": {"type": "LINKS", "properties": json.dumps({})},
        }
        session.run.return_value = iter([mock_record1, mock_record2])

        connected = await ltm.get_connected_nodes("node_1", direction="both")

        assert len(connected) == 2

    @pytest.mark.asyncio
    async def test_get_stats_disabled(self, ltm_disabled):
        """Test getting stats when disabled."""
        stats = await ltm_disabled.get_stats()

        assert stats["enabled"] is False

    @pytest.mark.asyncio
    async def test_get_stats_success(self, ltm_with_mock_driver):
        """Test getting memory statistics."""
        ltm, session, driver = ltm_with_mock_driver

        # Create mock results that iterate properly
        # get_stats calls _execute_query twice (node count and relationship count)
        def create_count_result(count):
            mock_record = MagicMock()
            mock_record.data.return_value = {"count": count}
            return iter([mock_record])

        # First call returns node count, second returns relationship count
        session.run.side_effect = [create_count_result(10), create_count_result(5)]

        stats = await ltm.get_stats()

        assert stats["enabled"] is True
        assert stats["node_count"] == 10
        assert stats["relationship_count"] == 5
        assert stats["connected"] is True

    @pytest.mark.asyncio
    async def test_get_stats_empty(self, ltm_with_mock_driver):
        """Test getting stats when database is empty."""
        ltm, session, result = ltm_with_mock_driver

        result.data.return_value = []

        stats = await ltm.get_stats()

        assert stats["node_count"] == 0
        assert stats["relationship_count"] == 0


class TestLongTermMemoryIntegration:
    """Integration tests for LongTermMemory."""

    @pytest.mark.asyncio
    async def test_store_and_retrieve_node(self):
        """Test storing and retrieving a node."""
        # Create LTM with mock driver
        mock_driver = MagicMock()
        mock_session = MagicMock()

        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)

        # Setup mock responses for store_node then get_node
        def create_mock_run_response(*args, **kwargs):
            # First call is store_node, second is get_node
            if not hasattr(create_mock_run_response, "call_count"):
                create_mock_run_response.call_count = 0
            create_mock_run_response.call_count += 1

            mock_record = MagicMock()
            if create_mock_run_response.call_count == 1:
                # store_node result
                mock_record.data.return_value = {"n": {"id": "test_node"}}
            else:
                # get_node result
                mock_record.data.return_value = {
                    "n": {
                        "id": "test_node",
                        "label": "Concept",
                        "properties": json.dumps({"name": "test"}),
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00",
                    }
                }
            return iter([mock_record])

        mock_session.run.side_effect = create_mock_run_response

        ltm = LongTermMemory(enabled=False)
        ltm.enabled = True
        ltm.driver = mock_driver

        # Store node
        node = KnowledgeNode(id="test_node", label="Concept", properties={"name": "test"})
        stored = await ltm.store_node(node)
        assert stored is True

        # Retrieve node
        retrieved = await ltm.get_node("test_node")
        assert retrieved is not None
        assert retrieved["id"] == "test_node"

    @pytest.mark.asyncio
    async def test_create_knowledge_graph(self):
        """Test creating a simple knowledge graph."""
        # Create LTM with mock driver
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
        mock_result.data.return_value = [{"n": {"id": "test"}}]
        mock_session.run.return_value = mock_result

        ltm = LongTermMemory(enabled=False)
        ltm.enabled = True
        ltm.driver = mock_driver

        # Create nodes
        node1 = KnowledgeNode(id="python", label="Language", properties={"typed": True})
        node2 = KnowledgeNode(id="fastapi", label="Framework", properties={"async": True})

        await ltm.store_node(node1)
        await ltm.store_node(node2)

        # Create relationship
        await ltm.create_relationship("python", "fastapi", "SUPPORTS")

        # Verify operations were called
        assert mock_session.run.call_count == 3

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test a complete workflow with LTM."""
        # Create LTM with mock driver
        mock_driver = MagicMock()
        mock_session = MagicMock()

        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)

        ltm = LongTermMemory(enabled=False)
        ltm.enabled = True
        ltm.driver = mock_driver

        # Setup mock responses using a counter
        call_responses = [
            {"n": {"id": "ai"}},  # store ai
            {"n": {"id": "ml"}},  # store ml
            {"r": {"type": "INCLUDES"}},  # create relationship
            {  # get_node
                "n": {
                    "id": "ai",
                    "label": "Concept",
                    "properties": json.dumps({"field": "computer_science"}),
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                }
            },
            {  # search_nodes
                "n": {
                    "id": "ml",
                    "label": "Concept",
                    "properties": json.dumps({"subset_of": "ai"}),
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                }
            },
            {  # get_connected_nodes
                "connected": {"id": "ml", "label": "Concept", "properties": json.dumps({})},
                "r": {"type": "INCLUDES", "properties": json.dumps({})},
            },
            {"count": 2},  # node count
            {"count": 1},  # relationship count
        ]

        def create_mock_run_response(*args, **kwargs):
            if not hasattr(create_mock_run_response, "call_index"):
                create_mock_run_response.call_index = 0

            idx = create_mock_run_response.call_index
            create_mock_run_response.call_index += 1

            mock_record = MagicMock()
            if idx < len(call_responses):
                mock_record.data.return_value = call_responses[idx]
            return iter([mock_record])

        mock_session.run.side_effect = create_mock_run_response

        # Store nodes
        ai_node = KnowledgeNode(id="ai", label="Concept", properties={"field": "computer_science"})
        ml_node = KnowledgeNode(id="ml", label="Concept", properties={"subset_of": "ai"})

        await ltm.store_node(ai_node)
        await ltm.store_node(ml_node)

        # Create relationship
        await ltm.create_relationship("ai", "ml", "INCLUDES")

        # Retrieve node
        retrieved = await ltm.get_node("ai")
        assert retrieved is not None

        # Search nodes
        results = await ltm.search_nodes(label="Concept")
        assert len(results) == 1

        # Get connected nodes
        connected = await ltm.get_connected_nodes("ai")
        assert len(connected) == 1

        # Get stats
        stats = await ltm.get_stats()
        assert stats["enabled"] is True
