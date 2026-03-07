"""
AEGIS Guardian Layer for OMNI-AI

Provides comprehensive security including:
- Input/output filtering and sanitization
- Content censorship and policy enforcement
- Intent analysis and threat detection
- Compliance checking and auditing
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import asyncio
from loguru import logger

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Content analysis will be limited.")


class SecurityLevel(Enum):
    """Security clearance levels."""
    LEVEL_1 = 1  # Safe Mode / Guest
    LEVEL_2 = 2  # Specialist / 2FA + Biometrics
    LEVEL_3 = 3  # Root Mode / Golden Key Protocol


class ThreatType(Enum):
    """Types of security threats."""
    MALICIOUS_CONTENT = "malicious_content"
    SENSITIVE_INFO_LEAK = "sensitive_info_leak"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    CODE_INJECTION = "code_injection"
    POLICY_VIOLATION = "policy_violation"
    BIASED_OUTPUT = "biased_output"


@dataclass
class SecurityEvent:
    """Security event record."""
    id: str
    event_type: ThreatType
    severity: str  # "low", "medium", "high", "critical"
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "severity": self.severity,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "metadata": self.metadata
        }


@dataclass
class FilterResult:
    """Result of content filtering."""
    is_safe: bool
    filtered_content: Optional[str] = None
    threats: List[ThreatType] = field(default_factory=list)
    confidence: float = 0.0
    action_taken: str = ""


class AegisGuardian:
    """
    AEGIS Guardian Layer - Comprehensive security system.
    
    Features:
    - Real-time content filtering
    - Intent analysis
    - Policy enforcement
    - Threat detection
    - Audit logging
    """
    
    # Regex patterns for detecting threats
    MALICIOUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript URLs
        r'on\w+\s*=',  # Event handlers
        r'eval\s*\(',  # eval() calls
        r'document\.',  # DOM manipulation
        r'window\.',  # Window object access
    ]
    
    SENSITIVE_PATTERNS = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{16}\b',  # Credit card
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP addresses
    ]
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.LEVEL_1):
        """
        Initialize AEGIS Guardian.
        
        Args:
            security_level: Default security clearance level
        """
        self.security_level = security_level
        self.security_events: List[SecurityEvent] = []
        self._lock = asyncio.Lock()
        
        # Compile regex patterns
        self.malicious_regex = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.MALICIOUS_PATTERNS]
        self.sensitive_regex = [re.compile(p) for p in self.SENSITIVE_PATTERNS]
        
        # Initialize content analysis models
        self.content_classifier = None
        self.sentiment_analyzer = None
        
        if TRANSFORMERS_AVAILABLE:
            self._initialize_models()
        
        logger.info(f"AEGIS Guardian initialized with security level: {security_level.name}")
    
    def _initialize_models(self) -> None:
        """Initialize ML models for content analysis."""
        try:
            # Content safety classifier
            self.content_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium"
            )
            
            logger.info("Content analysis models initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize content models: {e}")
    
    async def filter_input(
        self,
        content: str,
        user_clearance: SecurityLevel = SecurityLevel.LEVEL_1
    ) -> FilterResult:
        """
        Filter and sanitize input content.
        
        Args:
            content: Input content to filter
            user_clearance: User's security clearance level
            
        Returns:
            FilterResult with filtering outcome
        """
        threats = []
        filtered_content = content
        
        # Check for malicious patterns
        for pattern in self.malicious_regex:
            if pattern.search(content):
                threats.append(ThreatType.CODE_INJECTION)
                filtered_content = pattern.sub('[REDACTED]', filtered_content)
        
        # Check for sensitive information
        if self.security_level.value >= SecurityLevel.LEVEL_2.value:
            for pattern in self.sensitive_regex:
                if pattern.search(content):
                    threats.append(ThreatType.SENSITIVE_INFO_LEAK)
                    filtered_content = pattern.sub('[REDACTED]', filtered_content)
        
        # Analyze intent (if models available)
        if self.content_classifier and TRANSFORMERS_AVAILABLE:
            try:
                result = self.content_classifier(content[:512])  # Limit length
                if result[0]['label'] == 'malicious':
                    threats.append(ThreatType.MALICIOUS_CONTENT)
            except Exception as e:
                logger.debug(f"Intent analysis failed: {e}")
        
        # Determine if content is safe
        is_safe = len(threats) == 0
        
        # Log security event if threats found
        if threats:
            await self._log_security_event(
                event_type=threats[0],
                severity="high" if len(threats) > 1 else "medium",
                description=f"Threats detected in input: {[t.value for t in threats]}",
                metadata={"content_length": len(content), "threats": [t.value for t in threats]}
            )
        
        return FilterResult(
            is_safe=is_safe,
            filtered_content=filtered_content if not is_safe else content,
            threats=threats,
            confidence=0.8 if threats else 0.9,
            action_taken="filtered" if threats else "passed"
        )
    
    async def filter_output(
        self,
        content: str,
        user_clearance: SecurityLevel = SecurityLevel.LEVEL_1
    ) -> FilterResult:
        """
        Filter and sanitize output content.
        
        Args:
            content: Output content to filter
            user_clearance: User's security clearance level
            
        Returns:
            FilterResult with filtering outcome
        """
        threats = []
        filtered_content = content
        
        # Check for policy violations
        policy_violations = await self._check_policy_violations(content)
        if policy_violations:
            threats.extend(policy_violations)
        
        # Check for biased content
        if await self._detect_bias(content):
            threats.append(ThreatType.BIASED_OUTPUT)
        
        # Determine if content is safe
        is_safe = len(threats) == 0
        
        # Log security event if threats found
        if threats:
            await self._log_security_event(
                event_type=threats[0],
                severity="medium",
                description=f"Threats detected in output: {[t.value for t in threats]}",
                metadata={"content_length": len(content)}
            )
        
        return FilterResult(
            is_safe=is_safe,
            filtered_content=filtered_content if not is_safe else content,
            threats=threats,
            confidence=0.7 if threats else 0.95,
            action_taken="filtered" if threats else "passed"
        )
    
    async def _check_policy_violations(self, content: str) -> List[ThreatType]:
        """
        Check content against security policies.
        
        Args:
            content: Content to check
            
        Returns:
            List of policy violation threats
        """
        violations = []
        
        # Define prohibited content patterns
        prohibited_patterns = [
            (r'\bhow\s+to\s+(make|create|build)\s+(bomb|explosive|weapon|poison)', "dangerous content"),
            (r'\b(illegal|criminal|fraud)\b.*\b(instructions|how\s+to)', "illegal instructions"),
            (r'\b(hack|crack|bypass)\s+(security|authentication|password)', "security bypass"),
        ]
        
        for pattern, description in prohibited_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(ThreatType.POLICY_VIOLATION)
                logger.debug(f"Policy violation detected: {description}")
        
        return violations
    
    async def _detect_bias(self, content: str) -> bool:
        """
        Detect biased or discriminatory content.
        
        Args:
            content: Content to analyze
            
        Returns:
            True if bias detected, False otherwise
        """
        # Simplified bias detection - in production, use more sophisticated models
        biased_keywords = [
            "inferior", "superior", "subhuman", "degenerate",
            "parasite", "vermin", "animalistic"
        ]
        
        for keyword in biased_keywords:
            if keyword.lower() in content.lower():
                logger.debug(f"Potential bias detected: {keyword}")
                return True
        
        return False
    
    async def _log_security_event(
        self,
        event_type: ThreatType,
        severity: str,
        description: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            severity: Event severity
            description: Event description
            metadata: Additional metadata
        """
        event = SecurityEvent(
            id=f"sec_{datetime.utcnow().timestamp()}",
            event_type=event_type,
            severity=severity,
            description=description,
            metadata=metadata or {}
        )
        
        async with self._lock:
            self.security_events.append(event)
            
            # Keep only last 10,000 events
            if len(self.security_events) > 10000:
                self.security_events = self.security_events[-10000:]
        
        # Log based on severity
        if severity == "critical":
            logger.error(f"CRITICAL: {description}")
        elif severity == "high":
            logger.warning(f"HIGH: {description}")
        elif severity == "medium":
            logger.info(f"MEDIUM: {description}")
        else:
            logger.debug(f"LOW: {description}")
    
    async def get_security_events(
        self,
        limit: int = 100,
        event_type: Optional[ThreatType] = None,
        min_severity: Optional[str] = None
    ) -> List[SecurityEvent]:
        """
        Get security events.
        
        Args:
            limit: Maximum number of events to return
            event_type: Filter by event type
            min_severity: Filter by minimum severity
            
        Returns:
            List of security events
        """
        async with self._lock:
            events = self.security_events.copy()
        
        # Apply filters
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if min_severity:
            severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            min_level = severity_order.get(min_severity, 0)
            events = [e for e in events if severity_order.get(e.severity, 0) >= min_level]
        
        # Sort by timestamp (newest first) and limit
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        return events[:limit]
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get security statistics.
        
        Returns:
            Dictionary containing security statistics
        """
        async with self._lock:
            total_events = len(self.security_events)
            
            # Count events by type
            events_by_type = {}
            for event in self.security_events:
                event_type = event.event_type.value
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
            
            # Count events by severity
            events_by_severity = {}
            for event in self.security_events:
                severity = event.severity
                events_by_severity[severity] = events_by_severity.get(severity, 0) + 1
            
            return {
                "security_level": self.security_level.name,
                "total_events": total_events,
                "events_by_type": events_by_type,
                "events_by_severity": events_by_severity,
                "models_loaded": {
                    "content_classifier": self.content_classifier is not None,
                    "sentiment_analyzer": self.sentiment_analyzer is not None
                }
            }