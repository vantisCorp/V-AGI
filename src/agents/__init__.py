"""
OMNI-AI Agents Module

Contains all specialized agents for the multi-agent system:
- VERITAS: Truth verification and fact-checking
- LEX-Core: Legal and compliance analysis
- CERBERUS: Security monitoring and threat detection
- FORGE: Engineering and design
- VITA: Biological and medical analysis
- MUSE: Creative content generation
- ARES: Strategic planning and optimization
- LUDUS: Simulation and gaming
- ARGUS: Monitoring and analytics
"""

from .base_agent import AgentCapabilities, AgentResponse, AgentStatus, BaseAgent, Task, TaskPriority

__all__ = [
    "BaseAgent",
    "Task",
    "AgentResponse",
    "AgentStatus",
    "TaskPriority",
    "AgentCapabilities",
]
