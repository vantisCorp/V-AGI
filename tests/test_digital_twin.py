"""
Tests for Digital Twin Platform.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.tools.digital_twin import (
    DataSyncMode,
    DigitalTwin,
    TwinAlert,
    TwinEvent,
    TwinMetric,
    TwinModel,
    TwinState,
    TwinType,
)


class TestTwinType:
    """Test suite for TwinType enum."""

    def test_twin_type_values(self):
        """Test twin type values."""
        assert TwinType.ASSET.value == "asset"
        assert TwinType.SYSTEM.value == "system"
        assert TwinType.PROCESS.value == "process"
        assert TwinType.FACILITY.value == "facility"
        assert TwinType.NETWORK.value == "network"


class TestTwinState:
    """Test suite for TwinState enum."""

    def test_twin_state_values(self):
        """Test twin state values."""
        assert TwinState.INITIALIZING.value == "initializing"
        assert TwinState.ACTIVE.value == "active"
        assert TwinState.SYNCHRONIZING.value == "synchronizing"
        assert TwinState.SIMULATING.value == "simulating"
        assert TwinState.ERROR.value == "error"
        assert TwinState.OFFLINE.value == "offline"


class TestDataSyncMode:
    """Test suite for DataSyncMode enum."""

    def test_data_sync_mode_values(self):
        """Test data sync mode values."""
        assert DataSyncMode.REALTIME.value == "realtime"
        assert DataSyncMode.BATCH.value == "batch"
        assert DataSyncMode.EVENT_DRIVEN.value == "event_driven"
        assert DataSyncMode.MANUAL.value == "manual"


class TestTwinMetric:
    """Test suite for TwinMetric dataclass."""

    def test_twin_metric_creation(self):
        """Test creating a twin metric."""
        metric = TwinMetric(
            id="metric-1", name="temperature", value=25.5, unit="celsius", timestamp=datetime.now()
        )
        assert metric.id == "metric-1"
        assert metric.name == "temperature"
        assert metric.value == 25.5
        assert metric.unit == "celsius"

    def test_twin_metric_with_metadata(self):
        """Test twin metric with metadata."""
        metric = TwinMetric(
            id="metric-2",
            name="pressure",
            value=101.3,
            unit="kPa",
            timestamp=datetime.now(),
            metadata={"sensor": "sensor-1"},
        )
        assert metric.metadata == {"sensor": "sensor-1"}


class TestTwinEvent:
    """Test suite for TwinEvent dataclass."""

    def test_twin_event_creation(self):
        """Test creating a twin event."""
        event = TwinEvent(
            id="event-1",
            event_type="state_change",
            source="twin-1",
            data={"old_state": "active", "new_state": "error"},
            timestamp=datetime.now(),
        )
        assert event.id == "event-1"
        assert event.event_type == "state_change"
        assert event.source == "twin-1"
        assert event.severity == "info"

    def test_twin_event_with_severity(self):
        """Test twin event with severity."""
        event = TwinEvent(
            id="event-2",
            event_type="alert",
            source="twin-1",
            data={"message": "High temperature"},
            timestamp=datetime.now(),
            severity="warning",
        )
        assert event.severity == "warning"


class TestTwinAlert:
    """Test suite for TwinAlert dataclass."""

    def test_twin_alert_creation(self):
        """Test creating a twin alert."""
        alert = TwinAlert(
            id="alert-1",
            alert_type="threshold_exceeded",
            severity="high",
            message="Temperature exceeded threshold",
            data={"value": 100, "threshold": 80},
            timestamp=datetime.now(),
        )
        assert alert.id == "alert-1"
        assert alert.alert_type == "threshold_exceeded"
        assert alert.severity == "high"
        assert alert.acknowledged is False


class TestTwinModel:
    """Test suite for TwinModel dataclass."""

    def test_twin_model_creation(self):
        """Test creating a twin model."""
        model = TwinModel(
            id="model-1",
            name="Predictive Model",
            model_type="regression",
            accuracy=0.95,
            last_trained=datetime.now(),
            parameters={"epochs": 100},
        )
        assert model.id == "model-1"
        assert model.name == "Predictive Model"
        assert model.accuracy == 0.95


class TestDigitalTwin:
    """Test suite for Digital Twin Platform."""

    @pytest.fixture
    def platform(self):
        """Create digital twin platform instance."""
        return DigitalTwin()

    def test_init(self, platform):
        """Test initialization."""
        assert len(platform.twins) == 0
        assert len(platform.metrics) == 0
        assert len(platform.events) == 0
        assert len(platform.alerts) == 0
        assert len(platform.models) == 0

    @pytest.mark.asyncio
    async def test_create_twin(self, platform):
        """Test creating a digital twin."""
        twin = await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.ASSET,
            description="Test asset twin",
        )
        assert twin["id"] == "twin-1"
        assert twin["name"] == "Test Twin"
        assert twin["type"] == "asset"
        assert twin["state"] == "initializing"
        assert "twin-1" in platform.twins

    @pytest.mark.asyncio
    async def test_create_twin_duplicate(self, platform):
        """Test creating duplicate twin raises error."""
        await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.ASSET,
            description="Test asset twin",
        )

        with pytest.raises(ValueError, match="already exists"):
            await platform.create_twin(
                twin_id="twin-1",
                name="Duplicate Twin",
                twin_type=TwinType.ASSET,
                description="Duplicate twin",
            )

    @pytest.mark.asyncio
    async def test_update_metric(self, platform):
        """Test updating a metric."""
        await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.ASSET,
            description="Test asset twin",
        )

        metric = await platform.update_metric(
            twin_id="twin-1", metric_name="temperature", value=25.5, unit="celsius"
        )
        assert metric.name == "temperature"
        assert metric.value == 25.5
        assert metric.unit == "celsius"
        assert len(platform.metrics["twin-1"]) == 1

    @pytest.mark.asyncio
    async def test_update_metric_nonexistent_twin(self, platform):
        """Test updating metric for nonexistent twin."""
        with pytest.raises(ValueError, match="not found"):
            await platform.update_metric(
                twin_id="nonexistent", metric_name="temperature", value=25.5, unit="celsius"
            )

    @pytest.mark.asyncio
    async def test_sync_with_physical(self, platform):
        """Test synchronizing with physical system."""
        await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.SYSTEM,
            description="Test system twin",
        )

        physical_data = {
            "temperature": {"value": 30, "unit": "celsius"},
            "pressure": {"value": 101.3, "unit": "kPa"},
        }

        result = await platform.sync_with_physical("twin-1", physical_data)
        assert result is True
        assert platform.twins["twin-1"]["state"] == "active"
        assert platform.twins["twin-1"]["last_sync"] is not None

    @pytest.mark.asyncio
    async def test_sync_with_physical_nonexistent(self, platform):
        """Test syncing nonexistent twin."""
        with pytest.raises(ValueError, match="not found"):
            await platform.sync_with_physical("nonexistent", {})

    @pytest.mark.asyncio
    async def test_create_event(self, platform):
        """Test creating an event."""
        await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.ASSET,
            description="Test asset twin",
        )

        event = await platform.create_event(
            twin_id="twin-1", event_type="state_change", data={"new_state": "active"}
        )
        assert event.event_type == "state_change"
        assert event.source == "twin-1"
        assert len(platform.events) == 1

    @pytest.mark.asyncio
    async def test_create_alert(self, platform):
        """Test creating an alert."""
        await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.ASSET,
            description="Test asset twin",
        )

        alert = await platform.create_alert(
            twin_id="twin-1",
            alert_type="threshold_exceeded",
            message="High temperature detected",
            data={"value": 100},
        )
        assert alert.alert_type == "threshold_exceeded"
        assert alert.message == "High temperature detected"
        assert len(platform.alerts) == 1

    @pytest.mark.asyncio
    async def test_predict_metrics(self, platform):
        """Test predicting metrics."""
        await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.ASSET,
            description="Test asset twin",
        )

        # Add some metrics for prediction
        for i in range(5):
            await platform.update_metric(
                twin_id="twin-1", metric_name="temperature", value=20.0 + i, unit="celsius"
            )

        predictions = await platform.predict_metrics("twin-1", "temperature", horizon=5)
        assert len(predictions) == 5
        assert all("timestamp" in p for p in predictions)
        assert all("value" in p for p in predictions)

    @pytest.mark.asyncio
    async def test_predict_metrics_insufficient_data(self, platform):
        """Test prediction with insufficient data."""
        await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.ASSET,
            description="Test asset twin",
        )

        # Add only one metric
        await platform.update_metric(
            twin_id="twin-1", metric_name="temperature", value=25.0, unit="celsius"
        )

        predictions = await platform.predict_metrics("twin-1", "temperature")
        assert predictions == []

    @pytest.mark.asyncio
    async def test_predict_metrics_nonexistent_twin(self, platform):
        """Test prediction for nonexistent twin."""
        with pytest.raises(ValueError, match="not found"):
            await platform.predict_metrics("nonexistent", "temperature")

    @pytest.mark.asyncio
    async def test_simulate_scenario(self, platform):
        """Test simulating a scenario."""
        await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.ASSET,
            description="Test asset twin",
        )

        # Add baseline metrics
        await platform.update_metric("twin-1", "temperature", 25.0, "celsius")
        await platform.update_metric("twin-1", "pressure", 100.0, "kPa")

        scenario = {
            "duration": 60,
            "changes": {
                "temperature": {"type": "absolute", "value": 10},
                "pressure": {"type": "relative", "value": 0.1},
            },
        }

        result = await platform.simulate_scenario("twin-1", scenario)
        assert "scenario_id" in result
        assert "results" in result
        assert "temperature" in result["results"]
        assert result["results"]["temperature"]["simulated"] == 35.0

    @pytest.mark.asyncio
    async def test_simulate_scenario_nonexistent_twin(self, platform):
        """Test simulation for nonexistent twin."""
        with pytest.raises(ValueError, match="not found"):
            await platform.simulate_scenario("nonexistent", {})

    @pytest.mark.asyncio
    async def test_detect_anomalies(self, platform):
        """Test detecting anomalies."""
        await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.ASSET,
            description="Test asset twin",
        )

        # Add normal metrics
        for i in range(10):
            await platform.update_metric("twin-1", "temperature", 25.0 + i * 0.1, "celsius")

        # Add an anomalous value
        await platform.update_metric("twin-1", "temperature", 100.0, "celsius")

        anomalies = await platform.detect_anomalies("twin-1")
        assert len(anomalies) > 0
        assert anomalies[0]["metric_name"] == "temperature"

    @pytest.mark.asyncio
    async def test_detect_anomalies_nonexistent_twin(self, platform):
        """Test anomaly detection for nonexistent twin."""
        with pytest.raises(ValueError, match="not found"):
            await platform.detect_anomalies("nonexistent")

    @pytest.mark.asyncio
    async def test_register_event_callback(self, platform):
        """Test registering event callback."""
        callback = AsyncMock()
        platform.register_event_callback(callback)
        assert callback in platform.event_callbacks

    @pytest.mark.asyncio
    async def test_register_alert_callback(self, platform):
        """Test registering alert callback."""
        callback = AsyncMock()
        platform.register_alert_callback(callback)
        assert callback in platform.alert_callbacks

    @pytest.mark.asyncio
    async def test_get_twin_status(self, platform):
        """Test getting twin status."""
        await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.ASSET,
            description="Test asset twin",
        )

        status = await platform.get_twin_status("twin-1")
        assert status is not None
        assert "twin" in status
        assert status["twin"]["id"] == "twin-1"
        assert status["twin"]["state"] == "initializing"

    @pytest.mark.asyncio
    async def test_get_twin_status_nonexistent(self, platform):
        """Test getting status for nonexistent twin."""
        status = await platform.get_twin_status("nonexistent")
        assert status is None

    @pytest.mark.asyncio
    async def test_get_twin_status_with_metrics(self, platform):
        """Test getting twin status with metrics."""
        await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.ASSET,
            description="Test asset twin",
        )

        await platform.update_metric("twin-1", "temperature", 25.0, "celsius")

        status = await platform.get_twin_status("twin-1")
        assert status is not None
        assert "latest_metrics" in status
        assert "temperature" in status["latest_metrics"]
        assert status["metric_count"] == 1

    @pytest.mark.asyncio
    async def test_optimize_parameters(self, platform):
        """Test optimizing twin parameters."""
        await platform.create_twin(
            twin_id="twin-1",
            name="Test Twin",
            twin_type=TwinType.ASSET,
            description="Test asset twin",
        )

        await platform.update_metric("twin-1", "temperature", 25.0, "celsius")
        await platform.update_metric("twin-1", "pressure", 100.0, "kPa")

        result = await platform.optimize_parameters(
            "twin-1", {"temperature": "minimize", "pressure": "maximize"}
        )

        assert "twin_id" in result
        assert "recommendations" in result
        assert len(result["recommendations"]) == 2


class TestDigitalTwinIntegration:
    """Integration tests for Digital Twin Platform."""

    @pytest.mark.asyncio
    async def test_full_twin_lifecycle(self):
        """Test full twin lifecycle."""
        platform = DigitalTwin()

        # Create twin
        twin = await platform.create_twin(
            twin_id="factory-1",
            name="Factory Twin",
            twin_type=TwinType.FACILITY,
            description="Manufacturing facility digital twin",
        )
        assert twin["id"] == "factory-1"

        # Sync with physical data
        await platform.sync_with_physical(
            "factory-1",
            {
                "temperature": {"value": 22.5, "unit": "celsius"},
                "humidity": {"value": 45, "unit": "%"},
            },
        )

        # Create event
        await platform.create_event(
            twin_id="factory-1", event_type="startup", data={"operator": "John"}
        )

        # Simulate scenario
        await platform.update_metric("factory-1", "production_rate", 100, "units/hour")
        result = await platform.simulate_scenario(
            "factory-1", {"changes": {"production_rate": {"type": "relative", "value": 0.2}}}
        )

        assert "results" in result
        assert result["results"]["production_rate"]["simulated"] == 120.0

    @pytest.mark.asyncio
    async def test_multiple_twins(self):
        """Test managing multiple twins."""
        platform = DigitalTwin()

        # Create multiple twins
        for i in range(3):
            await platform.create_twin(
                twin_id=f"twin-{i}",
                name=f"Twin {i}",
                twin_type=TwinType.ASSET,
                description=f"Test twin {i}",
            )

        assert len(platform.twins) == 3

        # Add metrics to each
        for i in range(3):
            await platform.update_metric(f"twin-{i}", "status", i, "level")

        assert all(f"twin-{i}" in platform.metrics for i in range(3))
