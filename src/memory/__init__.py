"""
OMNI-AI Memory Module

Provides multi-tiered memory systems:
- Working Memory: Fast, temporary storage for active operations
- Long-Term Memory: Persistent, encrypted knowledge storage
- Vector Store: Similarity-based retrieval for semantic search
"""

from .working_memory import WorkingMemory, MemoryItem
from .long_term_memory import (
    LongTermMemory,
    KnowledgeNode,
    KnowledgeRelationship
)

__all__ = [
    "WorkingMemory",
    "MemoryItem",
    "LongTermMemory",
    "KnowledgeNode",
    "KnowledgeRelationship",
]