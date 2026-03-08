"""
Vector Store Module for OMNI-AI

Provides similarity-based semantic search and retrieval using
vector embeddings for efficient knowledge access.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from loguru import logger

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone not available. Vector store will be limited.")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("Sentence Transformers not available. Embedding generation will be limited.")


@dataclass
class VectorDocument:
    """Document stored in vector store."""
    id: str
    text: str
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "embedding": self.embedding.tolist() if self.embedding is not None else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class VectorStore:
    """
    Vector store implementation using Pinecone for similarity search.
    
    Provides:
    - Semantic similarity search
    - Embedding generation
    - Efficient retrieval of related documents
    - Metadata filtering
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        environment: Optional[str] = None,
        index_name: str = "omni-ai-vectors",
        dimension: int = 1536,
        enabled: bool = True
    ):
        """
        Initialize vector store.
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
            index_name: Name of the vector index
            dimension: Dimension of embeddings
            enabled: Enable or disable vector store
        """
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.dimension = dimension
        self.enabled = enabled and PINECONE_AVAILABLE
        self.index = None
        self.embedding_model = None
        
        if self.enabled:
            self._initialize()
    
    def _initialize(self) -> None:
        """Initialize vector store connection."""
        try:
            # Initialize Pinecone
            pinecone.init(
                api_key=self.api_key,
                environment=self.environment
            )
            
            # Get or create index
            if self.index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine"
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            
            self.index = pinecone.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
            # Initialize embedding model
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Initialized Sentence Transformer embedding model")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            self.enabled = False
    
    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        if self.embedding_model:
            return self.embedding_model.encode(text)
        return None
    
    async def add_document(
        self,
        document: VectorDocument
    ) -> bool:
        """
        Add document to vector store.
        
        Args:
            document: Document to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.warning("Vector store is disabled")
            return False
        
        try:
            # Generate embedding if not provided
            if document.embedding is None:
                document.embedding = self.generate_embedding(document.text)
            
            if document.embedding is None:
                logger.error(f"Failed to generate embedding for document: {document.id}")
                return False
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(
                    document.id,
                    document.embedding.tolist(),
                    {
                        "text": document.text,
                        "metadata": document.metadata,
                        "created_at": document.created_at.isoformat()
                    }
                )]
            )
            
            logger.debug(f"Added document to vector store: {document.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filters
            
        Returns:
            List of similar documents with scores
        """
        if not self.enabled:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            if query_embedding is None:
                logger.error("Failed to generate query embedding")
                return []
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding.tolist(),
                top_k=top_k,
                filter=filter_metadata,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "id": match.id,
                    "score": match.score,
                    "text": match.metadata.get("text", ""),
                    "metadata": match.metadata.get("metadata", {}),
                    "created_at": match.metadata.get("created_at", "")
                })
            
            logger.debug(f"Found {len(formatted_results)} results for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete document from vector store.
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            self.index.delete(ids=[document_id])
            logger.debug(f"Deleted document: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.
        
        Returns:
            Dictionary containing statistics
        """
        if not self.enabled:
            return {"enabled": False}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "enabled": True,
                "total_vectors": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", self.dimension),
                "index_name": self.index_name
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"enabled": True, "error": str(e)}