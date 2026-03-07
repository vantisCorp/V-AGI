# OMNI-AI Quick Start Guide

## Overview

OMNI-AI is a multi-agent AI system with 9 specialized agents designed to handle complex tasks across various domains. This guide will help you get started quickly.

---

## Installation

### Prerequisites
- Python 3.11 or higher
- Docker and Docker Compose
- Neo4j (for knowledge graph)
- Pinecone account (for vector search)
- Redis (for working memory)

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd omni-ai
   ```

2. **Run the setup script**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start services with Docker**
   ```bash
   docker-compose up -d
   ```

5. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## Basic Usage

### Starting OMNI-AI

```python
from src.main import OMNI_AI

# Initialize the system
omni_ai = OMNI_AI()

# Start the orchestrator
await omni_ai.start()
```

### Submitting Tasks

```python
from src.agents.base_agent import Task, TaskPriority

# Create a task
task = Task(
    task_id="task-001",
    description="Verify the following facts about climate change",
    parameters={
        "task_type": "fact_verification",
        "claims": [
            "Global temperatures have risen by 1.1°C since pre-industrial times",
            "CO2 levels are at their highest in 800,000 years"
        ]
    },
    priority=TaskPriority.MEDIUM
)

# Submit task to NEXUS orchestrator
result = await omni_ai.orchestrator.submit_task(task)
```

---

## Agent Reference

### 1. VERITAS - Truth Verification

**Use for**: Fact-checking, source validation, logical consistency

```python
task = Task(
    task_id="veritas-001",
    description="Verify claims about AI ethics",
    parameters={
        "task_type": "fact_verification",
        "claims": ["AI will replace all human jobs by 2030"]
    }
)
```

**Task Types**:
- `fact_verification`: Verify factual claims
- `logical_consistency`: Check argument validity
- `source_validation`: Evaluate source credibility
- `generate_citations`: Create citations
- `fact_check_content`: Comprehensive content verification

---

### 2. CERBERUS - Security Monitoring

**Use for**: Threat detection, anomaly monitoring, security auditing

```python
task = Task(
    task_id="cerberus-001",
    description="Monitor for security threats",
    parameters={
        "task_type": "monitor_threats",
        "target_system": "web_application",
        "duration": 3600  # 1 hour
    }
)
```

**Task Types**:
- `monitor_threats`: Real-time threat monitoring
- `detect_anomalies`: Identify unusual behavior
- `respond_to_incident`: Handle security incidents
- `scan_vulnerabilities`: System vulnerability assessment
- `monitor_compliance`: Security compliance tracking

---

### 3. MUSE - Creative Content

**Use for**: Content creation, creative writing, marketing materials

```python
task = Task(
    task_id="muse-001",
    description="Write a blog post about AI",
    parameters={
        "task_type": "create_article",
        "topic": "The Future of Artificial Intelligence",
        "tone": "informative",
        "length": 1000
    }
)
```

**Task Types**:
- `generate_story`: Create narratives
- `write_poetry`: Generate poetry
- `create_article`: Write articles
- `generate_marketing_copy`: Create marketing content
- `create_brand_content`: Develop brand materials
- `generate_social_media`: Platform-specific content
- `write_scripts`: Screenplay and dialogue
- `describe_art`: Art descriptions

---

### 4. FORGE - Engineering & Design

**Use for**: Design work, engineering calculations, material selection

```python
task = Task(
    task_id="forge-001",
    description="Design a bridge component",
    parameters={
        "task_type": "generate_blueprint",
        "component_type": "beam",
        "material": "steel",
        "load_requirements": "10000 kg"
    }
)
```

**Task Types**:
- `generate_blueprint`: Create technical blueprints
- `analyze_structure`: Structural analysis
- `select_materials`: Material recommendations
- `optimize_design`: Design optimization
- `qa_testing`: Quality assurance
- `recommend_prototyping`: Prototyping advice

---

### 5. VITA - Biological & Medical

**Use for**: Medical research, symptom analysis, drug interactions

```python
task = Task(
    task_id="vita-001",
    description="Analyze patient symptoms",
    parameters={
        "task_type": "analyze_symptoms",
        "symptoms": ["headache", "fever", "fatigue"],
        "patient_age": 35,
        "duration": "3 days"
    }
)
```

**Task Types**:
- `analyze_symptoms`: Symptom analysis
- `check_drug_interactions`: Drug interaction verification
- `analyze_patient_data`: Patient data interpretation
- `medical_research`: Research assistance
- `clinical_trial_analysis`: Clinical trial evaluation
- `epidemiology_study`: Disease pattern analysis
- `health_monitoring`: Health tracking

---

### 6. ARES - Strategic Planning

**Use for**: Business strategy, resource optimization, decision support

```python
task = Task(
    task_id="ares-001",
    description="Create a strategic plan for Q1",
    parameters={
        "task_type": "create_strategic_plan",
        "objectives": ["Increase market share by 10%"],
        "timeframe": "Q1 2025",
        "budget": 1000000
    }
)
```

**Task Types**:
- `create_strategic_plan`: Strategic planning
- `optimize_resources`: Resource allocation
- `assess_risk`: Risk evaluation
- `analyze_performance`: Performance metrics
- `optimize_supply_chain`: Supply chain improvement
- `decision_support`: Decision assistance
- `business_intelligence`: Market analysis
- `forecast_demand`: Demand prediction

---

### 7. LEX-Core - Legal & Compliance

**Use for**: Legal analysis, compliance checking, contract review

```python
task = Task(
    task_id="lex-001",
    description="Check GDPR compliance",
    parameters={
        "task_type": "compliance_assessment",
        "frameworks": ["gdpr"],
        "system_description": "Customer data processing system"
    }
)
```

**Task Types**:
- `legal_document_analysis`: Document analysis
- `compliance_assessment`: Compliance checking
- `contract_review`: Contract evaluation
- `regulatory_interpretation`: Regulatory explanation
- `risk_assessment`: Legal risk evaluation
- `policy_generation`: Policy creation
- `audit_preparation`: Audit readiness
- `intellectual_property_analysis`: IP analysis

**Supported Frameworks**:
- GDPR, CCPA, HIPAA, SOC2, ISO27001, NIST CSF, PCI DSS, EU AI Act, FERPA, COPPA

---

### 8. LUDUS - Simulation & Gaming

**Use for**: Simulations, modeling, game design

```python
task = Task(
    task_id="ludus-001",
    description="Simulate market dynamics",
    parameters={
        "task_type": "economic_modeling",
        "scenario": "market_growth",
        "time_horizon": 12  # months
    }
)
```

**Task Types**:
- `physics_simulation`: Physical systems
- `economic_modeling`: Economic behavior
- `game_mechanics_design`: Game systems
- `scenario_planning`: Scenario analysis
- `virtual_prototyping`: Prototyping
- `interactive_simulation`: User interaction
- `educational_game`: Educational content
- `strategic_war_game`: Strategy games

---

### 9. ARGUS - Monitoring & Analytics

**Use for**: System monitoring, performance analysis, alerting

```python
task = Task(
    task_id="argus-001",
    description="Monitor application performance",
    parameters={
        "task_type": "real_time_monitoring",
        "scope": "application",
        "metrics": ["response_time", "error_rate", "throughput"]
    }
)
```

**Task Types**:
- `real_time_monitoring`: Live monitoring
- `performance_analytics`: Performance analysis
- `log_analysis`: Log processing
- `alert_management`: Alert handling
- `trend_analysis`: Trend detection
- `anomaly_detection`: Anomaly identification
- `dashboard_generation`: Dashboard creation
- `report_generation`: Report creation

**Monitoring Scopes**:
- System, Application, Network, Security, Business, User Behavior

---

## Task Results

### Understanding AgentResponse

All tasks return an `AgentResponse` object:

```python
{
    "agent_id": "agent-identifier",
    "task_id": "task-identifier",
    "status": "COMPLETED",  # or FAILED
    "result": {
        # Task-specific results
        "status": "completed",
        "analysis": {...},
        "confidence": 0.85,
        "timestamp": "2025-01-18T10:30:00Z"
    },
    "timestamp": "2025-01-18T10:30:00Z"
}
```

### Handling Results

```python
# Check if task completed
if result.status == AgentStatus.COMPLETED:
    print("Task completed successfully!")
    
    # Access the result data
    analysis = result.result["analysis"]
    confidence = result.result["confidence"]
    
    print(f"Confidence: {confidence}")
    print(f"Analysis: {analysis}")
else:
    print(f"Task failed: {result.error}")
```

---

## Advanced Usage

### Multi-Agent Collaboration

The NEXUS orchestrator automatically coordinates multiple agents:

```python
# Complex task requiring multiple agents
complex_task = Task(
    task_id="complex-001",
    description="Research and write article",
    parameters={
        "task_type": "multi_agent",
        "subtasks": [
            {
                "agent": "VERITAS",
                "task": "fact_verification",
                "data": "claims to verify"
            },
            {
                "agent": "MUSE",
                "task": "create_article",
                "data": "topic and tone"
            }
        ]
    }
)

result = await omni_ai.orchestrator.submit_task(complex_task)
```

### Custom Agent Configuration

You can configure agent behavior:

```python
from src.agents.veritas import VERITASAgent

# Create agent with custom configuration
veritas = VERITASAgent()
veritas.config.update({
    "confidence_threshold": 0.9,
    "max_sources": 10,
    "verification_depth": "deep"
})
```

### Working with Memory Systems

```python
# Store data in working memory
await omni_ai.working_memory.set("key", {"data": "value"}, ttl=3600)

# Retrieve data
data = await omni_ai.working_memory.get("key")

# Store in long-term memory (knowledge graph)
await omni_ai.long_term_memory.store_node(
    node_id="node-001",
    node_type="concept",
    properties={"name": "AI", "domain": "technology"}
)

# Search vector store
results = await omni_ai.vector_store.search(
    query="artificial intelligence",
    top_k=5
)
```

---

## Error Handling

```python
from src.agents.base_agent import AgentStatus

try:
    result = await omni_ai.orchestrator.submit_task(task)
    
    if result.status == AgentStatus.FAILED:
        # Handle failure
        print(f"Task failed: {result.error}")
        
        # Check task history
        history = omni_ai.orchestrator.get_task_history(task.task_id)
        print(f"History: {history}")
        
except Exception as e:
    # Handle unexpected errors
    print(f"Unexpected error: {str(e)}")
```

---

## Performance Tips

### 1. Use Appropriate Task Priorities

```python
# High priority for urgent tasks
urgent_task = Task(
    task_id="urgent-001",
    description="Critical security scan",
    priority=TaskPriority.CRITICAL
)

# Low priority for background tasks
background_task = Task(
    task_id="bg-001",
    description="Generate report",
    priority=TaskPriority.LOW
)
```

### 2. Batch Similar Tasks

```python
# Submit multiple tasks efficiently
tasks = [Task(...) for _ in range(10)]
results = await omni_ai.orchestrator.submit_tasks(tasks)
```

### 3. Use Caching

```python
# Check working memory first
cached_result = await omni_ai.working_memory.get(cache_key)
if cached_result:
    return cached_result

# Otherwise, execute task
result = await omni_ai.orchestrator.submit_task(task)

# Cache the result
await omni_ai.working_memory.set(cache_key, result, ttl=3600)
```

---

## Monitoring and Debugging

### Check Agent Status

```python
# Get all registered agents
agents = omni_ai.orchestrator.get_agents()

for agent in agents:
    print(f"Agent: {agent.name}")
    print(f"Status: {agent.status}")
    print(f"Tasks Completed: {agent.metrics.tasks_completed}")
    print(f"Tasks Failed: {agent.metrics.tasks_failed}")
```

### View Task History

```python
# Get history for a specific task
history = omni_ai.orchestrator.get_task_history(task_id)
print(f"Task History: {history}")
```

### Access Logs

```python
# Logs are written to the configured log file
# Default: logs/omni_ai.log
```

---

## Security Considerations

### Clearance Levels

OMNI-AI uses a three-tier clearance system:

- **Level 1**: Basic access to public information
- **Level 2**: Access to sensitive but non-critical data
- **Level 3**: Access to critical and classified information

Ensure your agents have appropriate clearance:

```python
from src.agents.lex_core import LEXCoreAgent

# LEX-Core requires Level 2 clearance
lex_core = LEXCoreAgent()
assert lex_core.clearance_level >= 2
```

### AEGIS Security Layer

AEGIS automatically filters and monitors:

```python
# AEGIS is active by default
# It will:
# - Filter malicious inputs
# - Redact sensitive information
# - Detect policy violations
# - Log security events
```

---

## Troubleshooting

### Common Issues

**Issue**: Task fails with "Task validation failed"
- **Solution**: Check that required parameters are provided

**Issue**: Agent not responding
- **Solution**: Check agent status and restart if necessary

**Issue**: Memory operations failing
- **Solution**: Verify Redis and Neo4j are running

**Issue**: Low confidence scores
- **Solution**: Provide more detailed task descriptions

### Getting Help

- Check logs: `logs/omni_ai.log`
- Review documentation in `/docs/`
- Check IMPLEMENTATION_STATUS.md for known issues

---

## Best Practices

1. **Always check task status** before using results
2. **Use appropriate task priorities** for your use case
3. **Handle errors gracefully** with try-except blocks
4. **Cache frequently used results** in working memory
5. **Monitor agent performance** regularly
6. **Use specific task descriptions** for better results
7. **Validate input data** before submission
8. **Implement retry logic** for failed tasks
9. **Keep task history** for debugging
10. **Use memory systems** to share data between tasks

---

## Next Steps

1. Explore the full agent capabilities in SPECIALIZED_AGENTS_SUMMARY.md
2. Check IMPLEMENTATION_STATUS.md for project progress
3. Review the source code in `src/agents/` for details
4. Run the test suite: `pytest tests/`
5. Join the community for support and updates

---

## Additional Resources

- **Full Documentation**: See `README.md`
- **Agent Details**: `SPECIALIZED_AGENTS_SUMMARY.md`
- **Project Status**: `IMPLEMENTATION_STATUS.md`
- **API Reference**: Coming soon
- **Examples**: `examples/` directory

---

**Happy building with OMNI-AI!** 🚀