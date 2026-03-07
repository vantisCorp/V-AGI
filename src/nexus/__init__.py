"""
OMNI-AI NEXUS Module

Central orchestration system for multi-agent coordination:
- Task decomposition and distribution
- Agent selection and assignment
- Dependency management
- Resource optimization
- Progress tracking
"""

from .orchestrator import (
    NexusOrchestrator,
    TaskStatus,
    OrchestratedTask,
    AgentAssignment
)

__all__ = [
    "NexusOrchestrator",
    "TaskStatus",
    "OrchestratedTask",
    "AgentAssignment",
]