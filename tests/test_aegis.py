"""
Tests for AEGIS Guardian Layer.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.security.aegis import AegisGuardian, FilterResult, SecurityEvent, SecurityLevel, ThreatType


class TestSecurityLevel:
    """Test suite for SecurityLevel enum."""

    def test_security_level_values(self):
        """Test security level values."""
        assert SecurityLevel.LEVEL_1.value == 1
        assert SecurityLevel.LEVEL_2.value == 2
        assert SecurityLevel.LEVEL_3.value == 3


class TestThreatType:
    """Test suite for ThreatType enum."""

    def test_threat_type_values(self):
        """Test threat type values."""
        assert ThreatType.MALICIOUS_CONTENT.value == "malicious_content"
        assert ThreatType.SENSITIVE_INFO_LEAK.value == "sensitive_info_leak"
        assert ThreatType.UNAUTHORIZED_ACCESS.value == "unauthorized_access"
        assert ThreatType.CODE_INJECTION.value == "code_injection"
        assert ThreatType.POLICY_VIOLATION.value == "policy_violation"
        assert ThreatType.BIASED_OUTPUT.value == "biased_output"


class TestSecurityEvent:
    """Test suite for SecurityEvent dataclass."""

    def test_security_event_creation(self):
        """Test creating a security event."""
        event = SecurityEvent(
            id="test-1",
            event_type=ThreatType.CODE_INJECTION,
            severity="high",
            description="Test event",
        )
        assert event.id == "test-1"
        assert event.event_type == ThreatType.CODE_INJECTION
        assert event.severity == "high"
        assert event.description == "Test event"
        assert event.source == ""
        assert event.metadata == {}

    def test_security_event_to_dict(self):
        """Test converting event to dictionary."""
        event = SecurityEvent(
            id="test-2",
            event_type=ThreatType.POLICY_VIOLATION,
            severity="medium",
            description="Policy violation",
            source="test_source",
            metadata={"key": "value"},
        )
        result = event.to_dict()
        assert result["id"] == "test-2"
        assert result["event_type"] == "policy_violation"
        assert result["severity"] == "medium"
        assert result["description"] == "Policy violation"
        assert result["source"] == "test_source"
        assert result["metadata"] == {"key": "value"}
        assert "timestamp" in result


class TestFilterResult:
    """Test suite for FilterResult dataclass."""

    def test_filter_result_safe(self):
        """Test filter result for safe content."""
        result = FilterResult(
            is_safe=True,
            filtered_content="safe content",
            threats=[],
            confidence=0.95,
            action_taken="passed",
        )
        assert result.is_safe is True
        assert result.filtered_content == "safe content"
        assert result.threats == []
        assert result.confidence == 0.95

    def test_filter_result_unsafe(self):
        """Test filter result for unsafe content."""
        result = FilterResult(
            is_safe=False,
            filtered_content="[REDACTED]",
            threats=[ThreatType.CODE_INJECTION],
            confidence=0.8,
            action_taken="filtered",
        )
        assert result.is_safe is False
        assert result.filtered_content == "[REDACTED]"
        assert ThreatType.CODE_INJECTION in result.threats


class TestAegisGuardian:
    """Test suite for AEGIS Guardian."""

    @pytest.fixture
    def guardian(self):
        """Create guardian instance."""
        return AegisGuardian(security_level=SecurityLevel.LEVEL_1)

    def test_init(self, guardian):
        """Test initialization."""
        assert guardian.security_level == SecurityLevel.LEVEL_1
        assert len(guardian.security_events) == 0
        assert len(guardian.malicious_regex) > 0
        assert len(guardian.sensitive_regex) > 0

    def test_init_with_different_security_level(self):
        """Test initialization with different security level."""
        guardian = AegisGuardian(security_level=SecurityLevel.LEVEL_3)
        assert guardian.security_level == SecurityLevel.LEVEL_3

    @pytest.mark.asyncio
    async def test_filter_input_safe(self, guardian):
        """Test filtering safe input."""
        result = await guardian.filter_input("Hello, how are you?")
        assert result.is_safe is True
        assert result.action_taken == "passed"

    @pytest.mark.asyncio
    async def test_filter_input_script_injection(self, guardian):
        """Test detecting script injection."""
        result = await guardian.filter_input("<script>alert('xss')</script>")
        assert result.is_safe is False
        assert ThreatType.CODE_INJECTION in result.threats
        assert "[REDACTED]" in result.filtered_content

    @pytest.mark.asyncio
    async def test_filter_input_javascript_url(self, guardian):
        """Test detecting JavaScript URL."""
        result = await guardian.filter_input("javascript:void(0)")
        assert result.is_safe is False
        assert ThreatType.CODE_INJECTION in result.threats

    @pytest.mark.asyncio
    async def test_filter_input_eval(self, guardian):
        """Test detecting eval() calls."""
        result = await guardian.filter_input("eval(malicious_code)")
        assert result.is_safe is False
        assert ThreatType.CODE_INJECTION in result.threats

    @pytest.mark.asyncio
    async def test_filter_input_event_handler(self, guardian):
        """Test detecting event handlers."""
        result = await guardian.filter_input("onclick=alert('xss')")
        assert result.is_safe is False
        assert ThreatType.CODE_INJECTION in result.threats

    @pytest.mark.asyncio
    async def test_filter_input_sensitive_info_ssn(self):
        """Test detecting SSN in higher security level."""
        guardian = AegisGuardian(security_level=SecurityLevel.LEVEL_2)
        result = await guardian.filter_input("SSN: 123-45-6789")
        assert result.is_safe is False
        assert ThreatType.SENSITIVE_INFO_LEAK in result.threats

    @pytest.mark.asyncio
    async def test_filter_input_sensitive_info_email(self):
        """Test detecting email in higher security level."""
        guardian = AegisGuardian(security_level=SecurityLevel.LEVEL_2)
        result = await guardian.filter_input("Contact: test@example.com")
        assert result.is_safe is False
        assert ThreatType.SENSITIVE_INFO_LEAK in result.threats

    @pytest.mark.asyncio
    async def test_filter_input_sensitive_info_credit_card(self):
        """Test detecting credit card number in higher security level."""
        guardian = AegisGuardian(security_level=SecurityLevel.LEVEL_2)
        result = await guardian.filter_input("Card: 1234567890123456")
        assert result.is_safe is False
        assert ThreatType.SENSITIVE_INFO_LEAK in result.threats

    @pytest.mark.asyncio
    async def test_filter_output_safe(self, guardian):
        """Test filtering safe output."""
        result = await guardian.filter_output("This is a normal response.")
        assert result.is_safe is True
        assert result.action_taken == "passed"

    @pytest.mark.asyncio
    async def test_filter_output_policy_violation_dangerous(self, guardian):
        """Test detecting dangerous content policy violation."""
        result = await guardian.filter_output("how to make bomb")
        assert result.is_safe is False
        assert ThreatType.POLICY_VIOLATION in result.threats

    @pytest.mark.asyncio
    async def test_filter_output_policy_violation_illegal(self, guardian):
        """Test detecting illegal instructions policy violation."""
        result = await guardian.filter_output("illegal instructions for hacking")
        assert result.is_safe is False
        assert ThreatType.POLICY_VIOLATION in result.threats

    @pytest.mark.asyncio
    async def test_filter_output_policy_violation_bypass(self, guardian):
        """Test detecting security bypass policy violation."""
        result = await guardian.filter_output("how to hack password security")
        assert result.is_safe is False
        assert ThreatType.POLICY_VIOLATION in result.threats

    @pytest.mark.asyncio
    async def test_filter_output_bias_detection(self, guardian):
        """Test detecting biased content."""
        result = await guardian.filter_output("They are inferior to us")
        assert result.is_safe is False
        assert ThreatType.BIASED_OUTPUT in result.threats

    @pytest.mark.asyncio
    async def test_security_event_logging(self, guardian):
        """Test that security events are logged."""
        await guardian.filter_input("<script>alert('xss')</script>")

        events = await guardian.get_security_events()
        assert len(events) > 0
        assert events[0].event_type == ThreatType.CODE_INJECTION

    @pytest.mark.asyncio
    async def test_get_security_events_with_filter(self, guardian):
        """Test getting security events with filters."""
        # Generate some events - use patterns that match the actual regex
        await guardian.filter_input("<script>alert('xss')</script>")
        await guardian.filter_output("how to make bomb")

        events = await guardian.get_security_events(event_type=ThreatType.POLICY_VIOLATION)
        assert len(events) > 0
        assert all(e.event_type == ThreatType.POLICY_VIOLATION for e in events)

    @pytest.mark.asyncio
    async def test_get_security_events_with_severity_filter(self, guardian):
        """Test getting security events with severity filter."""
        # Generate some events
        await guardian.filter_input("<script>alert('xss')</script>")

        events = await guardian.get_security_events(min_severity="medium")
        assert len(events) > 0

    @pytest.mark.asyncio
    async def test_get_stats(self, guardian):
        """Test getting security statistics."""
        # Generate some events
        await guardian.filter_input("<script>alert('xss')</script>")
        await guardian.filter_output("how to make bomb")

        stats = await guardian.get_stats()
        assert "security_level" in stats
        assert "total_events" in stats
        assert stats["total_events"] >= 2
        assert "events_by_type" in stats
        assert "events_by_severity" in stats

    @pytest.mark.asyncio
    async def test_get_stats_empty(self, guardian):
        """Test getting security statistics when no events."""
        stats = await guardian.get_stats()
        assert stats["total_events"] == 0
        assert stats["events_by_type"] == {}
        assert stats["events_by_severity"] == {}


class TestAegisGuardianIntegration:
    """Integration tests for AEGIS Guardian."""

    @pytest.mark.asyncio
    async def test_full_filtering_workflow(self):
        """Test full filtering workflow."""
        guardian = AegisGuardian(security_level=SecurityLevel.LEVEL_2)

        # Input filtering
        input_result = await guardian.filter_input("Hello, my email is test@example.com")
        assert input_result.is_safe is False
        assert ThreatType.SENSITIVE_INFO_LEAK in input_result.threats

        # Output filtering
        output_result = await guardian.filter_output("Normal response without issues")
        assert output_result.is_safe is True

        # Check events
        events = await guardian.get_security_events()
        assert len(events) >= 1

    @pytest.mark.asyncio
    async def test_multiple_threats(self):
        """Test content with multiple threats."""
        guardian = AegisGuardian(security_level=SecurityLevel.LEVEL_2)

        result = await guardian.filter_input(
            "<script>alert('xss')</script> and my SSN is 123-45-6789"
        )
        assert result.is_safe is False
        assert len(result.threats) >= 2

    @pytest.mark.asyncio
    async def test_high_security_level(self):
        """Test with highest security level."""
        guardian = AegisGuardian(security_level=SecurityLevel.LEVEL_3)

        result = await guardian.filter_input("Normal content")
        assert result.is_safe is True

    @pytest.mark.asyncio
    async def test_event_limit(self):
        """Test that event limit is enforced."""
        guardian = AegisGuardian()

        # Add many events
        for i in range(100):
            await guardian.filter_input(f"<script>test{i}</script>")

        events = await guardian.get_security_events(limit=50)
        assert len(events) == 50
