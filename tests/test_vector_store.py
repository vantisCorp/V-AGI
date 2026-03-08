"""
Tests for Vector Store Module.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
from dataclasses import asdict

from src.memory.vector_store import (
    VectorDocument,
    VectorStore
)


class TestVectorDocument:
    """Tests for VectorDocument dataclass."""
    
    def test_vector_document_creation(self):
        """Test creating a VectorDocument."""
        doc = VectorDocument(
            id="doc_1",
            text="This is a test document",
            metadata={"source": "test", "page": 1}
        )
        
        assert doc.id == "doc_1"
        assert doc.text == "This is a test document"
        assert doc.embedding is None
        assert doc.metadata["source"] == "test"
        assert isinstance(doc.created_at, datetime)
    
    def test_vector_document_with_embedding(self):
        """Test creating VectorDocument with embedding."""
        embedding = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        doc = VectorDocument(
            id="doc_2",
            text="Embedded document",
            embedding=embedding
        )
        
        assert doc.embedding is not None
        assert len(doc.embedding) == 5
    
    def test_vector_document_to_dict(self):
        """Test VectorDocument to_dict method."""
        embedding = np.array([1.0, 2.0, 3.0])
        doc = VectorDocument(
            id="doc_3",
            text="Test",
            embedding=embedding,
            metadata={"key": "value"}
        )
        
        result = doc.to_dict()
        
        assert result["id"] == "doc_3"
        assert result["text"] == "Test"
        assert result["embedding"] == [1.0, 2.0, 3.0]
        assert result["metadata"]["key"] == "value"
        assert "created_at" in result
    
    def test_vector_document_to_dict_no_embedding(self):
        """Test VectorDocument to_dict without embedding."""
        doc = VectorDocument(
            id="doc_4",
            text="No embedding"
        )
        
        result = doc.to_dict()
        
        assert result["embedding"] is None
    
    def test_vector_document_default_values(self):
        """Test VectorDocument default values."""
        doc = VectorDocument(id="doc_5", text="Test")
        
        assert doc.metadata == {}
        assert doc.embedding is None
        assert isinstance(doc.created_at, datetime)


class TestVectorStore:
    """Tests for VectorStore class."""
    
    @pytest.fixture
    def vs_disabled(self):
        """Create a VectorStore with disabled state."""
        return VectorStore(enabled=False)
    
    @pytest.fixture
    def vs_with_mock_index(self):
        """Create a VectorStore with mocked index."""
        mock_index = MagicMock()
        
        vs = VectorStore(enabled=False)
        vs.enabled = True
        vs.index = mock_index
        vs.embedding_model = None
        
        return vs, mock_index
    
    def test_vs_initialization_disabled(self, vs_disabled):
        """Test VectorStore initialization when disabled."""
        assert vs_disabled.enabled is False
        assert vs_disabled.index is None
    
    def test_vs_initialization_with_config(self):
        """Test VectorStore initialization with custom config."""
        vs = VectorStore(
            api_key="test_key",
            environment="test_env",
            index_name="test_index",
            dimension=512,
            enabled=False
        )
        
        assert vs.api_key == "test_key"
        assert vs.environment == "test_env"
        assert vs.index_name == "test_index"
        assert vs.dimension == 512
    
    def test_generate_embedding_no_model(self, vs_disabled):
        """Test generating embedding without model."""
        result = vs_disabled.generate_embedding("test text")
        
        assert result is None
    
    def test_generate_embedding_with_model(self):
        """Test generating embedding with mock model."""
        vs = VectorStore(enabled=False)
        vs.embedding_model = MagicMock()
        vs.embedding_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        
        result = vs.generate_embedding("test text")
        
        assert result is not None
        vs.embedding_model.encode.assert_called_once_with("test text")
    
    @pytest.mark.asyncio
    async def test_add_document_disabled(self, vs_disabled):
        """Test adding document when disabled."""
        doc = VectorDocument(id="doc_1", text="Test")
        
        result = await vs_disabled.add_document(doc)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_add_document_success(self, vs_with_mock_index):
        """Test successfully adding a document."""
        vs, mock_index = vs_with_mock_index
        
        # Mock embedding generation
        vs.embedding_model = MagicMock()
        vs.embedding_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        
        doc = VectorDocument(
            id="doc_1",
            text="Test document",
            metadata={"source": "test"}
        )
        
        result = await vs.add_document(doc)
        
        assert result is True
        mock_index.upsert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_document_with_embedding(self, vs_with_mock_index):
        """Test adding document with pre-computed embedding."""
        vs, mock_index = vs_with_mock_index
        
        doc = VectorDocument(
            id="doc_2",
            text="Test",
            embedding=np.array([0.1, 0.2, 0.3])
        )
        
        result = await vs.add_document(doc)
        
        assert result is True
        mock_index.upsert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_document_no_embedding_model(self, vs_with_mock_index):
        """Test adding document without embedding model."""
        vs, mock_index = vs_with_mock_index
        
        doc = VectorDocument(id="doc_3", text="Test")
        
        result = await vs.add_document(doc)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_add_document_exception(self, vs_with_mock_index):
        """Test adding document with exception."""
        vs, mock_index = vs_with_mock_index
        mock_index.upsert.side_effect = Exception("Upsert failed")
        
        doc = VectorDocument(
            id="doc_4",
            text="Test",
            embedding=np.array([0.1, 0.2, 0.3])
        )
        
        result = await vs.add_document(doc)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_search_disabled(self, vs_disabled):
        """Test searching when disabled."""
        result = await vs_disabled.search("test query")
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_search_success(self, vs_with_mock_index):
        """Test successful search."""
        vs, mock_index = vs_with_mock_index
        
        # Mock embedding generation
        vs.embedding_model = MagicMock()
        vs.embedding_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        
        # Mock search results
        mock_match = MagicMock()
        mock_match.id = "doc_1"
        mock_match.score = 0.95
        mock_match.metadata = {
            "text": "Test document",
            "metadata": {"source": "test"},
            "created_at": "2024-01-01T00:00:00"
        }
        
        mock_results = MagicMock()
        mock_results.matches = [mock_match]
        mock_index.query.return_value = mock_results
        
        results = await vs.search("test query", top_k=5)
        
        assert len(results) == 1
        assert results[0]["id"] == "doc_1"
        assert results[0]["score"] == 0.95
        mock_index.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_with_filter(self, vs_with_mock_index):
        """Test search with metadata filter."""
        vs, mock_index = vs_with_mock_index
        
        # Mock embedding generation
        vs.embedding_model = MagicMock()
        vs.embedding_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        
        # Mock empty results
        mock_results = MagicMock()
        mock_results.matches = []
        mock_index.query.return_value = mock_results
        
        results = await vs.search(
            "test query",
            top_k=10,
            filter_metadata={"category": "tech"}
        )
        
        # Verify filter was passed
        call_kwargs = mock_index.query.call_args[1]
        assert call_kwargs["filter"] == {"category": "tech"}
    
    @pytest.mark.asyncio
    async def test_search_no_embedding_model(self, vs_with_mock_index):
        """Test search without embedding model."""
        vs, mock_index = vs_with_mock_index
        
        results = await vs.search("test query")
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_search_exception(self, vs_with_mock_index):
        """Test search with exception."""
        vs, mock_index = vs_with_mock_index
        
        vs.embedding_model = MagicMock()
        vs.embedding_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        mock_index.query.side_effect = Exception("Query failed")
        
        results = await vs.search("test query")
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_delete_document_disabled(self, vs_disabled):
        """Test deleting document when disabled."""
        result = await vs_disabled.delete_document("doc_1")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self, vs_with_mock_index):
        """Test successfully deleting a document."""
        vs, mock_index = vs_with_mock_index
        
        result = await vs.delete_document("doc_1")
        
        assert result is True
        mock_index.delete.assert_called_once_with(ids=["doc_1"])
    
    @pytest.mark.asyncio
    async def test_delete_document_exception(self, vs_with_mock_index):
        """Test deleting document with exception."""
        vs, mock_index = vs_with_mock_index
        mock_index.delete.side_effect = Exception("Delete failed")
        
        result = await vs.delete_document("doc_1")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_stats_disabled(self, vs_disabled):
        """Test getting stats when disabled."""
        stats = await vs_disabled.get_stats()
        
        assert stats["enabled"] is False
    
    @pytest.mark.asyncio
    async def test_get_stats_success(self, vs_with_mock_index):
        """Test getting vector store statistics."""
        vs, mock_index = vs_with_mock_index
        
        mock_index.describe_index_stats.return_value = {
            "total_vector_count": 100,
            "dimension": 1536
        }
        
        stats = await vs.get_stats()
        
        assert stats["enabled"] is True
        assert stats["total_vectors"] == 100
        assert stats["dimension"] == 1536
        assert stats["index_name"] == "omni-ai-vectors"
    
    @pytest.mark.asyncio
    async def test_get_stats_exception(self, vs_with_mock_index):
        """Test getting stats with exception."""
        vs, mock_index = vs_with_mock_index
        mock_index.describe_index_stats.side_effect = Exception("Stats failed")
        
        stats = await vs.get_stats()
        
        assert stats["enabled"] is True
        assert "error" in stats


class TestVectorStoreIntegration:
    """Integration tests for VectorStore."""
    
    @pytest.mark.asyncio
    async def test_add_and_search_workflow(self):
        """Test adding a document and searching for it."""
        mock_index = MagicMock()
        
        vs = VectorStore(enabled=False)
        vs.enabled = True
        vs.index = mock_index
        vs.embedding_model = MagicMock()
        
        # Mock embedding generation
        vs.embedding_model.encode.return_value = np.array([0.5, 0.5, 0.5])
        
        # Add document
        doc = VectorDocument(
            id="search_doc",
            text="Machine learning is fascinating",
            metadata={"category": "tech"}
        )
        
        added = await vs.add_document(doc)
        assert added is True
        
        # Mock search results
        mock_match = MagicMock()
        mock_match.id = "search_doc"
        mock_match.score = 0.99
        mock_match.metadata = {
            "text": "Machine learning is fascinating",
            "metadata": {"category": "tech"},
            "created_at": "2024-01-01T00:00:00"
        }
        
        mock_results = MagicMock()
        mock_results.matches = [mock_match]
        mock_index.query.return_value = mock_results
        
        # Search
        results = await vs.search("machine learning", top_k=5)
        
        assert len(results) == 1
        assert results[0]["id"] == "search_doc"
    
    @pytest.mark.asyncio
    async def test_full_crud_workflow(self):
        """Test full CRUD workflow."""
        mock_index = MagicMock()
        
        vs = VectorStore(enabled=False)
        vs.enabled = True
        vs.index = mock_index
        vs.embedding_model = MagicMock()
        vs.embedding_model.encode.return_value = np.array([0.1, 0.2, 0.3])
        
        # Create
        doc = VectorDocument(
            id="crud_doc",
            text="Document for CRUD test",
            metadata={"test": True}
        )
        
        added = await vs.add_document(doc)
        assert added is True
        
        # Read (via search)
        mock_match = MagicMock()
        mock_match.id = "crud_doc"
        mock_match.score = 1.0
        mock_match.metadata = {
            "text": "Document for CRUD test",
            "metadata": {"test": True},
            "created_at": "2024-01-01T00:00:00"
        }
        
        mock_results = MagicMock()
        mock_results.matches = [mock_match]
        mock_index.query.return_value = mock_results
        
        results = await vs.search("CRUD test")
        assert len(results) == 1
        
        # Delete
        deleted = await vs.delete_document("crud_doc")
        assert deleted is True
        
        # Verify stats
        mock_index.describe_index_stats.return_value = {"total_vector_count": 0}
        stats = await vs.get_stats()
        assert stats["enabled"] is True