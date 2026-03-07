"""
Digital Twin Platform Module
Provides virtual replica capabilities for physical systems and assets.
Supports real-time synchronization, predictive analytics, and scenario simulation.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json
from datetime import datetime
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwinType(Enum):
    """Types of digital twins."""
    ASSET = "asset"
    SYSTEM = "system"
    PROCESS = "process"
    FACILITY = "facility"
    NETWORK = "network"


class TwinState(Enum):
    """States of a digital twin."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SYNCHRONIZING = "synchronizing"
    SIMULATING = "simulating"
    ERROR = "error"
    OFFLINE = "offline"


class DataSyncMode(Enum):
    """Data synchronization modes."""
    REALTIME = "realtime"
    BATCH = "batch"
    EVENT_DRIVEN = "event_driven"
    MANUAL = "manual"


@dataclass
class TwinMetric:
    """Represents a metric in the digital twin."""
    id: str
    name: str
    value: Any
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TwinEvent:
    """Represents an event in the digital twin."""
    id: str
    event_type: str
    source: str
    data: Dict[str, Any]
    timestamp: datetime
    severity: str = "info"


@dataclass
class TwinAlert:
    """Represents an alert in the digital twin."""
    id: str
    alert_type: str
    severity: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    acknowledged: bool = False


@dataclass
class TwinModel:
    """Represents a predictive model for the twin."""
    id: str
    name: str
    model_type: str
    accuracy: float
    last_trained: datetime
    parameters: Dict[str, Any]


class DigitalTwin:
    """
    Digital Twin Platform for OMNI-AI.
    
    Provides comprehensive digital twin capabilities including:
    - Real-time synchronization with physical assets
    - Predictive analytics and forecasting
    - Scenario simulation and what-if analysis
    - Anomaly detection and alerting
    - Performance optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Digital Twin Platform.
        
        Args:
            config: Configuration dictionary for twin settings
        """
        self.config = config or {}
        
        # Twin registry
        self.twins: Dict[str, Dict[str, Any]] = {}
        self.metrics: Dict[str, List[TwinMetric]] = {}
        self.events: List[TwinEvent] = []
        self.alerts: List[TwinAlert] = []
        self.models: Dict[str, TwinModel] = {}
        
        # Callbacks for events and alerts
        self.event_callbacks: List[Callable] = []
        self.alert_callbacks: List[Callable] = []
        
        logger.info("Digital Twin Platform initialized")
    
    async def create_twin(self,
                         twin_id: str,
                         name: str,
                         twin_type: TwinType,
                         description: str,
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new digital twin.
        
        Args:
            twin_id: Unique identifier for the twin
            name: Name of the twin
            twin_type: Type of digital twin
            description: Description of the physical system
            metadata: Additional metadata
            
        Returns:
            Twin configuration dictionary
        """
        if twin_id in self.twins:
            raise ValueError(f"Twin {twin_id} already exists")
        
        twin = {
            "id": twin_id,
            "name": name,
            "type": twin_type.value,
            "description": description,
            "state": TwinState.INITIALIZING.value,
            "sync_mode": DataSyncMode.REALTIME.value,
            "created_at": datetime.now().isoformat(),
            "last_sync": None,
            "metadata": metadata or {}
        }
        
        self.twins[twin_id] = twin
        self.metrics[twin_id] = []
        
        logger.info(f"Created digital twin: {name} ({twin_id})")
        return twin
    
    async def update_metric(self,
                           twin_id: str,
                           metric_name: str,
                           value: Any,
                           unit: str,
                           metadata: Optional[Dict[str, Any]] = None) -> TwinMetric:
        """
        Update a metric for a digital twin.
        
        Args:
            twin_id: ID of the twin
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            metadata: Additional metadata
            
        Returns:
            TwinMetric object
        """
        if twin_id not in self.twins:
            raise ValueError(f"Twin {twin_id} not found")
        
        metric_id = f"metric_{len(self.metrics[twin_id])}"
        
        metric = TwinMetric(
            id=metric_id,
            name=metric_name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.metrics[twin_id].append(metric)
        
        # Check for anomalies
        await self._check_anomalies(twin_id, metric)
        
        logger.debug(f"Updated metric {metric_name} for twin {twin_id}")
        return metric
    
    async def sync_with_physical(self,
                                twin_id: str,
                                physical_data: Dict[str, Any]) -> bool:
        """
        Synchronize twin with physical system data.
        
        Args:
            twin_id: ID of the twin
            physical_data: Data from physical system
            
        Returns:
            Success status
        """
        if twin_id not in self.twins:
            raise ValueError(f"Twin {twin_id} not found")
        
        self.twins[twin_id]["state"] = TwinState.SYNCHRONIZING.value
        
        try:
            # Update metrics from physical data
            for key, value in physical_data.items():
                if isinstance(value, dict):
                    # Handle nested data
                    unit = value.get("unit", "")
                    val = value.get("value", value)
                    metadata = {k: v for k, v in value.items() if k not in ["unit", "value"]}
                else:
                    unit = ""
                    val = value
                    metadata = {}
                
                await self.update_metric(twin_id, key, val, unit, metadata)
            
            self.twins[twin_id]["last_sync"] = datetime.now().isoformat()
            self.twins[twin_id]["state"] = TwinState.ACTIVE.value
            
            logger.info(f"Synchronized twin {twin_id} with physical system")
            return True
            
        except Exception as e:
            self.twins[twin_id]["state"] = TwinState.ERROR.value
            logger.error(f"Sync error for twin {twin_id}: {e}")
            return False
    
    async def create_event(self,
                          twin_id: str,
                          event_type: str,
                          data: Dict[str, Any],
                          severity: str = "info") -> TwinEvent:
        """
        Create an event for a digital twin.
        
        Args:
            twin_id: ID of the twin
            event_type: Type of event
            data: Event data
            severity: Event severity (info, warning, error, critical)
            
        Returns:
            TwinEvent object
        """
        event_id = f"event_{len(self.events)}"
        
        event = TwinEvent(
            id=event_id,
            event_type=event_type,
            source=twin_id,
            data=data,
            timestamp=datetime.now(),
            severity=severity
        )
        
        self.events.append(event)
        
        # Trigger event callbacks
        for callback in self.event_callbacks:
            try:
                await callback(event)
            except Exception as e:
                logger.error(f"Event callback error: {e}")
        
        logger.info(f"Created event {event_type} for twin {twin_id}")
        return event
    
    async def create_alert(self,
                          twin_id: str,
                          alert_type: str,
                          message: str,
                          data: Dict[str, Any],
                          severity: str = "warning") -> TwinAlert:
        """
        Create an alert for a digital twin.
        
        Args:
            twin_id: ID of the twin
            alert_type: Type of alert
            message: Alert message
            data: Alert data
            severity: Alert severity (info, warning, error, critical)
            
        Returns:
            TwinAlert object
        """
        alert_id = f"alert_{len(self.alerts)}"
        
        alert = TwinAlert(
            id=alert_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            data=data,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        
        # Trigger alert callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
        
        logger.warning(f"Created alert {alert_type} for twin {twin_id}: {message}")
        return alert
    
    async def predict_metrics(self,
                            twin_id: str,
                            metric_name: str,
                            horizon: int = 10) -> List[Dict[str, Any]]:
        """
        Predict future values of a metric using predictive models.
        
        Args:
            twin_id: ID of the twin
            metric_name: Name of the metric to predict
            horizon: Number of time steps to predict
            
        Returns:
            List of predicted values with timestamps
        """
        if twin_id not in self.twins:
            raise ValueError(f"Twin {twin_id} not found")
        
        # Get historical metric data
        historical_metrics = [
            m for m in self.metrics.get(twin_id, [])
            if m.name == metric_name
        ]
        
        if len(historical_metrics) < 2:
            return []
        
        # Simple linear prediction (in real implementation, use ML models)
        predictions = []
        
        try:
            # Get last few values for trend analysis
            recent_values = [float(m.value) for m in historical_metrics[-5:]]
            
            # Calculate trend
            if len(recent_values) >= 2:
                trend = (recent_values[-1] - recent_values[0]) / len(recent_values)
            else:
                trend = 0
            
            # Generate predictions
            last_value = recent_values[-1]
            last_time = historical_metrics[-1].timestamp
            
            for i in range(1, horizon + 1):
                predicted_value = last_value + trend * i
                predicted_time = last_time.timestamp() + i * 60  # 1 minute intervals
                
                predictions.append({
                    "timestamp": predicted_time,
                    "value": predicted_value,
                    "confidence": max(0.5, 1.0 - i * 0.05)  # Decreasing confidence
                })
            
            logger.info(f"Generated {len(predictions)} predictions for {metric_name}")
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
        
        return predictions
    
    async def simulate_scenario(self,
                               twin_id: str,
                               scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate a scenario on the digital twin.
        
        Args:
            twin_id: ID of the twin
            scenario: Scenario definition (changes, conditions, duration)
            
        Returns:
            Simulation results
        """
        if twin_id not in self.twins:
            raise ValueError(f"Twin {twin_id} not found")
        
        self.twins[twin_id]["state"] = TwinState.SIMULATING.value
        
        try:
            # Get baseline metrics
            baseline_metrics = self.metrics.get(twin_id, [])
            
            # Apply scenario changes
            changes = scenario.get("changes", {})
            duration = scenario.get("duration", 60)  # seconds
            
            simulation_results = {
                "scenario_id": f"scenario_{len(self.events)}",
                "twin_id": twin_id,
                "duration": duration,
                "changes": changes,
                "results": {},
                "impact": {}
            }
            
            # Simulate each changed metric
            for metric_name, change in changes.items():
                change_type = change.get("type", "absolute")
                change_value = change.get("value", 0)
                
                # Find current value
                current_metrics = [m for m in baseline_metrics if m.name == metric_name]
                if current_metrics:
                    current_value = float(current_metrics[-1].value)
                    
                    # Apply change
                    if change_type == "absolute":
                        new_value = current_value + change_value
                    elif change_type == "relative":
                        new_value = current_value * (1 + change_value)
                    else:
                        new_value = change_value
                    
                    # Calculate impact
                    impact = (new_value - current_value) / current_value if current_value != 0 else 0
                    
                    simulation_results["results"][metric_name] = {
                        "baseline": current_value,
                        "simulated": new_value,
                        "change": new_value - current_value,
                        "impact_percent": impact * 100
                    }
            
            self.twins[twin_id]["state"] = TwinState.ACTIVE.value
            
            logger.info(f"Simulated scenario for twin {twin_id}")
            return simulation_results
            
        except Exception as e:
            self.twins[twin_id]["state"] = TwinState.ERROR.value
            logger.error(f"Simulation error: {e}")
            return {"error": str(e)}
    
    async def detect_anomalies(self, twin_id: str) -> List[Dict[str, Any]]:
        """
        Detect anomalies in twin metrics.
        
        Args:
            twin_id: ID of the twin
            
        Returns:
            List of detected anomalies
        """
        if twin_id not in self.twins:
            raise ValueError(f"Twin {twin_id} not found")
        
        anomalies = []
        
        for metric_name in set(m.name for m in self.metrics.get(twin_id, [])):
            metrics = [m for m in self.metrics[twin_id] if m.name == metric_name]
            
            if len(metrics) < 3:
                continue
            
            # Calculate statistics
            values = [float(m.value) for m in metrics]
            mean = sum(values) / len(values)
            std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
            
            # Check last value for anomaly (3-sigma rule)
            last_value = values[-1]
            if std > 0 and abs(last_value - mean) > 3 * std:
                anomalies.append({
                    "metric_name": metric_name,
                    "value": last_value,
                    "expected_range": [mean - 3 * std, mean + 3 * std],
                    "severity": "high" if abs(last_value - mean) > 4 * std else "medium",
                    "timestamp": metrics[-1].timestamp.isoformat()
                })
        
        return anomalies
    
    async def _check_anomalies(self, twin_id: str, metric: TwinMetric):
        """Check for anomalies in a metric and create alerts if needed."""
        anomalies = await self.detect_anomalies(twin_id)
        
        for anomaly in anomalies:
            if anomaly["metric_name"] == metric.name:
                await self.create_alert(
                    twin_id,
                    "anomaly_detected",
                    f"Anomaly detected in {metric.name}",
                    anomaly,
                    anomaly["severity"]
                )
    
    async def get_twin_status(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a digital twin.
        
        Args:
            twin_id: ID of the twin
            
        Returns:
            Twin status dictionary
        """
        if twin_id not in self.twins:
            return None
        
        twin = self.twins[twin_id]
        metrics = self.metrics.get(twin_id, [])
        
        # Get latest metrics
        latest_metrics = {}
        for metric_name in set(m.name for m in metrics):
            metric_list = [m for m in metrics if m.name == metric_name]
            if metric_list:
                latest = metric_list[-1]
                latest_metrics[metric_name] = {
                    "value": latest.value,
                    "unit": latest.unit,
                    "timestamp": latest.timestamp.isoformat()
                }
        
        return {
            "twin": twin,
            "latest_metrics": latest_metrics,
            "metric_count": len(metrics),
            "event_count": len([e for e in self.events if e.source == twin_id]),
            "alert_count": len([a for a in self.alerts if a.data.get("twin_id") == twin_id])
        }
    
    async def optimize_parameters(self,
                                 twin_id: str,
                                 objectives: Dict[str, str]) -> Dict[str, Any]:
        """
        Optimize twin parameters based on objectives.
        
        Args:
            twin_id: ID of the twin
            objectives: Optimization objectives (minimize/maximize metrics)
            
        Returns:
            Optimization recommendations
        """
        if twin_id not in self.twins:
            raise ValueError(f"Twin {twin_id} not found")
        
        recommendations = {
            "twin_id": twin_id,
            "objectives": objectives,
            "recommendations": []
        }
        
        # Analyze metrics and generate recommendations
        for metric_name, objective in objectives.items():
            metrics = [m for m in self.metrics.get(twin_id, []) if m.name == metric_name]
            
            if not metrics:
                continue
            
            values = [float(m.value) for m in metrics]
            trend = (values[-1] - values[0]) / len(values) if len(values) > 1 else 0
            
            recommendation = {
                "metric": metric_name,
                "current_value": values[-1],
                "trend": "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable",
                "objective": objective
            }
            
            # Generate specific recommendations
            if objective == "minimize" and trend > 0:
                recommendation["action"] = "reduce_parameters"
                recommendation["priority"] = "high"
            elif objective == "maximize" and trend < 0:
                recommendation["action"] = "increase_parameters"
                recommendation["priority"] = "high"
            else:
                recommendation["action"] = "maintain_current"
                recommendation["priority"] = "low"
            
            recommendations["recommendations"].append(recommendation)
        
        logger.info(f"Generated optimization recommendations for twin {twin_id}")
        return recommendations
    
    def register_event_callback(self, callback: Callable):
        """Register a callback for twin events."""
        self.event_callbacks.append(callback)
    
    def register_alert_callback(self, callback: Callable):
        """Register a callback for twin alerts."""
        self.alert_callbacks.append(callback)


async def main():
    """Example usage of Digital Twin Platform."""
    twin_platform = DigitalTwin()
    
    # Create a digital twin
    twin = await twin_platform.create_twin(
        "motor_001",
        "Industrial Motor",
        TwinType.ASSET,
        "Large industrial motor for manufacturing"
    )
    
    # Sync with physical data
    await twin_platform.sync_with_physical(
        "motor_001",
        {
            "temperature": {"value": 85.5, "unit": "°C"},
            "vibration": {"value": 2.3, "unit": "mm/s"},
            "speed": {"value": 1800, "unit": "RPM"}
        }
    )
    
    # Predict future values
    predictions = await twin_platform.predict_metrics("motor_001", "temperature", horizon=5)
    print(f"Predictions: {json.dumps(predictions, indent=2)}")
    
    # Simulate scenario
    scenario_result = await twin_platform.simulate_scenario(
        "motor_001",
        {
            "changes": {
                "speed": {"type": "relative", "value": 0.1}
            },
            "duration": 30
        }
    )
    print(f"Scenario result: {json.dumps(scenario_result, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())