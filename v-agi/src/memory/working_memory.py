"""
Working Memory Module for OMNI-AI

Provides temporary storage for active tasks, intermediate results,
and contextual information used during agent operations.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict
import asyncio
from loguru import logger


@dataclass
class MemoryItem:
    """Item stored in working memory."""
    key: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ttl: Optional[int] = None  # Time to live in seconds
    
    def is_expired(self) -> bool:
        """Check if item has expired."""
        if self.ttl is None:
            return False
        return datetime.utcnow() > self.timestamp + timedelta(seconds=self.ttl)


class WorkingMemory:
    """
    Working memory implementation using LRU cache with TTL support.
    
    Provides fast access to frequently used data with automatic
    cleanup of expired items.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        """
        Initialize working memory.
        
        Args:
            max_size: Maximum number of items to store
            default_ttl: Default time-to-live for items in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, MemoryItem] = OrderedDict()
        self._lock = asyncio.Lock()
        
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in working memory.
        
        Args:
            key: Key to store value under
            value: Value to store
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        async with self._lock:
            # Remove existing key if present (to update position)
            if key in self._cache:
                del self._cache[key]
            
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl
            
            # Create new memory item
            item = MemoryItem(key=key, value=value, ttl=ttl)
            
            # Check if cache is full
            if len(self._cache) >= self.max_size:
                # Remove oldest item
                self._cache.popitem(last=False)
            
            # Add new item (most recently used)
            self._cache[key] = item
            logger.debug(f"Stored item in working memory: {key}")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from working memory.
        
        Args:
            key: Key to retrieve
            
        Returns:
            Value if found and not expired, None otherwise
        """
        async with self._lock:
            if key not in self._cache:
                return None
            
            item = self._cache[key]
            
            # Check if expired
            if item.is_expired():
                del self._cache[key]
                logger.debug(f"Removed expired item: {key}")
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return item.value
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from working memory.
        
        Args:
            key: Key to delete
            
        Returns:
            True if key was found and deleted, False otherwise
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Deleted item: {key}")
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all items from working memory."""
        async with self._lock:
            self._cache.clear()
            logger.info("Working memory cleared")
    
    async def cleanup_expired(self) -> int:
        """
        Remove all expired items from memory.
        
        Returns:
            Number of items removed
        """
        async with self._lock:
            expired_keys = [
                key for key, item in self._cache.items()
                if item.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired items")
            
            return len(expired_keys)
    
    async def get_keys(self) -> List[str]:
        """
        Get all keys in working memory.
        
        Returns:
            List of keys
        """
        async with self._lock:
            return list(self._cache.keys())
    
    async def get_size(self) -> int:
        """
        Get current number of items in memory.
        
        Returns:
            Number of items stored
        """
        async with self._lock:
            return len(self._cache)
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary containing memory statistics
        """
        async with self._lock:
            expired_count = sum(1 for item in self._cache.values() if item.is_expired())
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "usage_percent": (len(self._cache) / self.max_size) * 100,
                "expired_items": expired_count,
                "default_ttl": self.default_ttl
            }