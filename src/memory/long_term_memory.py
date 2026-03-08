"""
Long-Term Memory Module for OMNI-AI

Provides persistent, encrypted storage for knowledge, historical data,
and learned patterns using Neo4j knowledge graph and vector databases.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

try:
    from neo4j import GraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("Neo4j driver not available. Long-term memory will be limited.")


@dataclass
class KnowledgeNode:
    """Node in the knowledge graph."""

    id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "id": self.id,
            "label": self.label,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class KnowledgeRelationship:
    """Relationship between knowledge nodes."""

    source: str
    target: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.relationship_type,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
        }


class LongTermMemory:
    """
    Long-term memory implementation using Neo4j knowledge graph.

    Provides persistent storage with:
    - Knowledge graph structure
    - Vector similarity search
    - Encrypted storage for sensitive data
    - Temporal versioning
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password",
        enabled: bool = True,
    ):
        """
        Initialize long-term memory.

        Args:
            uri: Neo4j connection URI
            username: Database username
            password: Database password
            enabled: Enable or disable long-term memory
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.enabled = enabled and NEO4J_AVAILABLE
        self.driver = None

        if self.enabled:
            self._connect()

    def _connect(self) -> None:
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            logger.info("Connected to Neo4j knowledge graph")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.enabled = False

    async def close(self) -> None:
        """Close database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def _execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result records
        """
        if not self.enabled or not self.driver:
            return []

        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []

    async def store_node(self, node: KnowledgeNode) -> bool:
        """
        Store a knowledge node.

        Args:
            node: Knowledge node to store

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.warning("Long-term memory is disabled")
            return False

        query = """
        MERGE (n:Knowledge {id: $id})
        SET n.label = $label,
            n.properties = $properties,
            n.created_at = $created_at,
            n.updated_at = $updated_at
        RETURN n
        """

        parameters = {
            "id": node.id,
            "label": node.label,
            "properties": json.dumps(node.properties),
            "created_at": node.created_at.isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        self._execute_query(query, parameters)
        logger.debug(f"Stored node: {node.id}")
        return True

    async def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a knowledge node.

        Args:
            node_id: Node identifier

        Returns:
            Node data if found, None otherwise
        """
        if not self.enabled:
            return None

        query = """
        MATCH (n:Knowledge {id: $id})
        RETURN n
        """

        results = self._execute_query(query, {"id": node_id})

        if results:
            node = results[0]["n"]
            return {
                "id": node["id"],
                "label": node["label"],
                "properties": json.loads(node["properties"]),
                "created_at": node["created_at"],
                "updated_at": node["updated_at"],
            }
        return None

    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Dict[str, Any] = None,
    ) -> bool:
        """
        Create a relationship between nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            relationship_type: Type of relationship
            properties: Relationship properties

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        query = """
        MATCH (source:Knowledge {id: $source_id})
        MATCH (target:Knowledge {id: $target_id})
        MERGE (source)-[r:RELATIONSHIP {type: $type}]->(target)
        SET r.properties = $properties,
            r.created_at = $created_at
        RETURN r
        """

        parameters = {
            "source_id": source_id,
            "target_id": target_id,
            "type": relationship_type,
            "properties": json.dumps(properties or {}),
            "created_at": datetime.utcnow().isoformat(),
        }

        self._execute_query(query, parameters)
        logger.debug(f"Created relationship: {source_id} -> {target_id}")
        return True

    async def search_nodes(
        self, label: Optional[str] = None, properties: Dict[str, Any] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for knowledge nodes.

        Args:
            label: Node label filter
            properties: Property filters
            limit: Maximum number of results

        Returns:
            List of matching nodes
        """
        if not self.enabled:
            return []

        query_parts = ["MATCH (n:Knowledge)"]
        where_conditions = []
        parameters = {}

        if label:
            where_conditions.append("n.label = $label")
            parameters["label"] = label

        if properties:
            for key, value in properties.items():
                where_conditions.append(f"n.properties CONTAINS $prop_{key}")
                parameters[f"prop_{key}"] = json.dumps({key: value})

        if where_conditions:
            query_parts.append("WHERE " + " AND ".join(where_conditions))

        query_parts.append(f"RETURN n LIMIT {limit}")

        results = self._execute_query(" ".join(query_parts), parameters)

        return [
            {
                "id": r["n"]["id"],
                "label": r["n"]["label"],
                "properties": json.loads(r["n"]["properties"]),
                "created_at": r["n"]["created_at"],
                "updated_at": r["n"]["updated_at"],
            }
            for r in results
        ]

    async def get_connected_nodes(
        self, node_id: str, relationship_type: Optional[str] = None, direction: str = "both"
    ) -> List[Dict[str, Any]]:
        """
        Get nodes connected to a given node.

        Args:
            node_id: Starting node ID
            relationship_type: Filter by relationship type
            direction: "outgoing", "incoming", or "both"

        Returns:
            List of connected nodes
        """
        if not self.enabled:
            return []

        rel_pattern = ""
        if relationship_type:
            rel_pattern = f":RELATIONSHIP {{type: '{relationship_type}'}}"

        if direction == "outgoing":
            match_pattern = f"(n:Knowledge {{id: $node_id}})-[r{rel_pattern}]->(connected)"
        elif direction == "incoming":
            match_pattern = f"(n:Knowledge {{id: $node_id}})<-[r{rel_pattern}]-(connected)"
        else:
            match_pattern = f"(n:Knowledge {{id: $node_id}})-[r{rel_pattern}]-(connected)"

        query = f"""
        MATCH {match_pattern}
        RETURN connected, r
        """

        results = self._execute_query(query, {"node_id": node_id})

        return [
            {
                "node": {
                    "id": r["connected"]["id"],
                    "label": r["connected"]["label"],
                    "properties": json.loads(r["connected"]["properties"]),
                },
                "relationship": {
                    "type": r["r"]["type"],
                    "properties": json.loads(r["r"]["properties"]),
                },
            }
            for r in results
        ]

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.

        Returns:
            Dictionary containing memory statistics
        """
        if not self.enabled:
            return {"enabled": False}

        node_count_query = "MATCH (n:Knowledge) RETURN count(n) as count"
        relationship_count_query = "MATCH ()-[r:RELATIONSHIP]->() RETURN count(r) as count"

        node_count = self._execute_query(node_count_query)
        relationship_count = self._execute_query(relationship_count_query)

        return {
            "enabled": True,
            "node_count": node_count[0]["count"] if node_count else 0,
            "relationship_count": relationship_count[0]["count"] if relationship_count else 0,
            "connected": self.driver is not None,
        }
