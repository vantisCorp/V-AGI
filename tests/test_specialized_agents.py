"""
Tests for Specialized Agents
Tests all 9 specialized agents in the OMNI-AI system
"""

import pytest
from unittest.mock import Mock, patch
from src.agents.base_agent import Task, TaskPriority

from src.agents.veritas import VeritasAgent
from src.agents.cerberus import CerberusAgent
from src.agents.muse import MuseAgent
from src.agents.forge import ForgeAgent
from src.agents.vita import VitaAgent
from src.agents.ares import AresAgent
from src.agents.lex_core import LEXCoreAgent
from src.agents.ludus import LUDUSAgent
from src.agents.argus import ARGUSAgent


class TestVeritasAgent:
    """Test suite for VERITAS Agent (Truth Verification)."""
    
    @pytest.fixture
    def agent(self):
        """Create VERITAS agent instance."""
        return VeritasAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "veritas"
        assert hasattr(agent, 'trusted_sources')
    
    @pytest.mark.asyncio
    async def test_validate_task(self, agent):
        """Test task validation."""
        task = Task(
            id="test_task",
            description="Verify a fact",
            parameters={"claim": "The Earth is round"},
            priority=TaskPriority.MEDIUM
        )
        result = await agent.validate_task(task)
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_execute_verify_fact(self, agent):
        """Test fact verification task."""
        task = Task(
            id="test_fact_1",
            description="Verify a fact",
            parameters={"claim": "The Earth is round", "task_type": "verify_fact"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert response.agent_id == "veritas"
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_check_consistency(self, agent):
        """Test consistency check task."""
        task = Task(
            id="test_consistency_1",
            description="Check consistency",
            parameters={"content": "All cats are mammals. Some mammals are cats.", "task_type": "check_consistency"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_validate_sources(self, agent):
        """Test source validation task."""
        task = Task(
            id="test_sources_1",
            description="Validate sources",
            parameters={"sources": ["https://example.com"], "task_type": "validate_sources"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_generate_citations(self, agent):
        """Test citation generation task."""
        task = Task(
            id="test_citations_1",
            description="Generate citations",
            parameters={"content": "Research shows that...", "task_type": "generate_citations"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_fact_check_content(self, agent):
        """Test content fact-checking task."""
        task = Task(
            id="test_factcheck_1",
            description="Fact check content",
            parameters={"content": "The Earth is 4.5 billion years old.", "task_type": "fact_check_content"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_unknown_task_type(self, agent):
        """Test handling of unknown task type."""
        task = Task(
            id="test_unknown_1",
            description="Unknown task",
            parameters={"task_type": "unknown_type"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        # VERITAS returns result with error for unknown types
        assert response.result is not None


class TestCerberusAgent:
    """Test suite for CERBERUS Agent (Security)."""
    
    @pytest.fixture
    def agent(self):
        """Create CERBERUS agent instance."""
        return CerberusAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "cerberus"
    
    @pytest.mark.asyncio
    async def test_validate_task(self, agent):
        """Test task validation."""
        task = Task(
            id="test_task",
            description="Monitor security",
            parameters={"action": "scan"},
            priority=TaskPriority.HIGH
        )
        result = await agent.validate_task(task)
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """Test security task execution."""
        task = Task(
            id="test_task",
            description="Monitor security",
            parameters={"action": "scan", "task_type": "monitor_threats"},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'status')

    @pytest.mark.asyncio
    async def test_execute_detect_anomalies(self, agent):
        """Test anomaly detection task."""
        task = Task(
            id="test_anomaly_1",
            description="Detect anomalies",
            parameters={
                "task_type": "detect_anomalies",
                "data_sources": ["network_logs", "system_logs"],
                "sensitivity": "high"
            },
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_respond_incident(self, agent):
        """Test incident response task."""
        task = Task(
            id="test_incident_1",
            description="Respond to incident",
            parameters={
                "task_type": "respond_incident",
                "incident_type": "malware_detection",
                "severity": "high",
                "affected_systems": ["server-1", "workstation-5"]
            },
            priority=TaskPriority.CRITICAL
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_scan_vulnerabilities(self, agent):
        """Test vulnerability scanning task."""
        task = Task(
            id="test_vuln_1",
            description="Scan vulnerabilities",
            parameters={
                "task_type": "scan_vulnerabilities",
                "target_systems": ["web-server", "database-server"],
                "scan_depth": "deep"
            },
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_check_compliance(self, agent):
        """Test compliance check task."""
        task = Task(
            id="test_compliance_1",
            description="Check compliance",
            parameters={
                "task_type": "check_compliance",
                "framework": "ISO27001",
                "scope": ["access_control", "encryption", "incident_management"]
            },
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_generate_security_report(self, agent):
        """Test security report generation task."""
        task = Task(
            id="test_report_1",
            description="Generate security report",
            parameters={
                "task_type": "generate_security_report",
                "report_type": "executive_summary",
                "period": "Q1 2024"
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_unknown_task_type(self, agent):
        """Test unknown task type handling."""
        task = Task(
            id="test_unknown_sec_1",
            description="Unknown task",
            parameters={"task_type": "unknown_security_type"},
            priority=TaskPriority.LOW
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert "error" in response.result

    @pytest.mark.asyncio
    async def test_validate_task_success(self, agent):
        """Test task validation with valid task type."""
        task = Task(
            id="test_validate_sec_1",
            description="Valid task",
            parameters={"task_type": "monitor_threats"},
            priority=TaskPriority.HIGH
        )
        is_valid = await agent.validate_task(task)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_task_invalid(self, agent):
        """Test task validation with invalid task type."""
        task = Task(
            id="test_validate_sec_2",
            description="Invalid task",
            parameters={"task_type": "invalid_type"},
            priority=TaskPriority.MEDIUM
        )
        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_get_stats(self, agent):
        """Test get_stats method."""
        stats = await agent.get_stats()
        assert stats is not None
        assert "total_incidents" in stats
        assert "threat_indicators_configured" in stats

    @pytest.mark.asyncio
    async def test_threat_indicators_initialized(self, agent):
        """Test threat indicators are initialized."""
        assert agent.threat_indicators is not None
        assert len(agent.threat_indicators) > 0


class TestMuseAgent:
    """Test suite for MUSE Agent (Creative)."""
    
    @pytest.fixture
    def agent(self):
        """Create MUSE agent instance."""
        return MuseAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "muse"
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """Test creative task execution."""
        task = Task(
            id="test_task",
            description="Generate content",
            parameters={"content_type": "story", "topic": "AI", "task_type": "generate_content"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'status')

    @pytest.mark.asyncio
    async def test_execute_generate_story(self, agent):
        """Test story generation task."""
        task = Task(
            id="test_story_1",
            description="Generate a story",
            parameters={
                "task_type": "generate_story",
                "genre": "science fiction",
                "length": "short",
                "characters": ["hero", "villain"]
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_generate_poem(self, agent):
        """Test poem generation task."""
        task = Task(
            id="test_poem_1",
            description="Generate a poem",
            parameters={
                "task_type": "generate_poem",
                "topic": "nature",
                "style": "haiku",
                "stanzas": 3
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_write_article(self, agent):
        """Test article writing task."""
        task = Task(
            id="test_article_1",
            description="Write an article",
            parameters={
                "task_type": "write_article",
                "topic": "Artificial Intelligence",
                "tone": "informative",
                "word_count": 500
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_create_marketing_copy(self, agent):
        """Test marketing copy creation task."""
        task = Task(
            id="test_marketing_1",
            description="Create marketing copy",
            parameters={
                "task_type": "create_marketing_copy",
                "product": "Smart Watch",
                "target_audience": "young professionals",
                "key_benefits": ["fitness tracking", "notifications", "style"]
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_design_brand_identity(self, agent):
        """Test brand identity design task."""
        task = Task(
            id="test_brand_1",
            description="Design brand identity",
            parameters={
                "task_type": "design_brand_identity",
                "brand_name": "TechCorp",
                "industry": "technology",
                "values": ["innovation", "reliability", "sustainability"]
            },
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_generate_social_media(self, agent):
        """Test social media content generation task."""
        task = Task(
            id="test_social_1",
            description="Generate social media content",
            parameters={
                "task_type": "generate_social_media",
                "platform": "twitter",
                "content_type": "promotional",
                "campaign_theme": "Summer Sale"
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_write_script(self, agent):
        """Test script writing task."""
        task = Task(
            id="test_script_1",
            description="Write a script",
            parameters={
                "task_type": "write_script",
                "format": "video",
                "duration": "60 seconds",
                "topic": "Product demonstration"
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_describe_art(self, agent):
        """Test art description task."""
        task = Task(
            id="test_art_1",
            description="Describe art",
            parameters={
                "task_type": "describe_art",
                "style": "impressionist",
                "subject": "landscape",
                "mood": "peaceful"
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_unknown_task_type(self, agent):
        """Test unknown task type handling."""
        task = Task(
            id="test_unknown_1",
            description="Unknown task",
            parameters={"task_type": "unknown_creative_type"},
            priority=TaskPriority.LOW
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert "error" in response.result

    @pytest.mark.asyncio
    async def test_validate_task_success(self, agent):
        """Test task validation with valid task type."""
        task = Task(
            id="test_validate_1",
            description="Valid task",
            parameters={"task_type": "generate_story"},
            priority=TaskPriority.MEDIUM
        )
        is_valid = await agent.validate_task(task)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_task_invalid(self, agent):
        """Test task validation with invalid task type."""
        task = Task(
            id="test_validate_2",
            description="Invalid task",
            parameters={"task_type": "invalid_type"},
            priority=TaskPriority.MEDIUM
        )
        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_get_stats(self, agent):
        """Test get_stats method."""
        stats = await agent.get_stats()
        assert stats is not None
        assert "content_types_supported" in stats
        assert "specialization" in stats


class TestForgeAgent:
    """Test suite for FORGE Agent (Design & Engineering)."""
    
    @pytest.fixture
    def agent(self):
        """Create FORGE agent instance."""
        return ForgeAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "forge"
        assert hasattr(agent, 'material_database')
    
    @pytest.mark.asyncio
    async def test_execute_generate_blueprint(self, agent):
        """Test blueprint generation task."""
        task = Task(
            id="test_blueprint_1",
            description="Generate blueprint",
            parameters={"component_type": "bracket", "task_type": "generate_blueprint"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert response.agent_id == "forge"
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_analyze_structure(self, agent):
        """Test structure analysis task."""
        task = Task(
            id="test_structure_1",
            description="Analyze structure",
            parameters={"structure_type": "beam", "task_type": "analyze_structure"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_select_materials(self, agent):
        """Test material selection task."""
        task = Task(
            id="test_materials_1",
            description="Select materials",
            parameters={"requirements": {"strength": "high"}, "task_type": "select_materials"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_create_design(self, agent):
        """Test design creation task."""
        task = Task(
            id="test_design_1",
            description="Create design",
            parameters={"design_type": "component", "task_type": "create_design"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_optimize_design(self, agent):
        """Test design optimization task."""
        task = Task(
            id="test_optimize_1",
            description="Optimize design",
            parameters={"design_id": "D123", "task_type": "optimize_design"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_quality_assurance(self, agent):
        """Test quality assurance task."""
        task = Task(
            id="test_qa_1",
            description="Quality assurance",
            parameters={"design_id": "D456", "task_type": "quality_assurance"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_prototype_recommendation(self, agent):
        """Test prototype recommendation task."""
        task = Task(
            id="test_proto_1",
            description="Prototype recommendation",
            parameters={"design_id": "D789", "task_type": "prototype_recommendation"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_calculate_stress(self, agent):
        """Test stress calculation task."""
        task = Task(
            id="test_stress_1",
            description="Calculate stress",
            parameters={"component_type": "beam", "task_type": "calculate_stress"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_unknown_task_type(self, agent):
        """Test handling of unknown task type."""
        task = Task(
            id="test_unknown_1",
            description="Unknown task",
            parameters={"task_type": "unknown_type"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        # FORGE returns result with error for unknown types
        assert response.result is not None
    
    @pytest.mark.asyncio
    async def test_get_stats(self, agent):
        """Test getting agent statistics."""
        stats = await agent.get_stats()
        assert stats is not None
        assert "specialization" in stats
        assert stats["specialization"] == "engineering"


class TestVitaAgent:
    """Test suite for VITA Agent (Healthcare)."""
    
    @pytest.fixture
    def agent(self):
        """Create VITA agent instance."""
        return VitaAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "vita"
        assert hasattr(agent, 'conditions_database')
        assert hasattr(agent, 'drug_interactions')
    
    @pytest.mark.asyncio
    async def test_execute_symptom_analysis(self, agent):
        """Test symptom analysis task."""
        task = Task(
            id="test_symptoms_1",
            description="Analyze symptoms",
            parameters={"symptoms": ["fever", "cough"], "task_type": "analyze_symptoms"},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert response.agent_id == "vita"
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_drug_interactions(self, agent):
        """Test drug interaction check task."""
        task = Task(
            id="test_drug_1",
            description="Check drug interactions",
            parameters={"task_type": "check_drug_interactions", "medications": ["aspirin", "ibuprofen"]},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_patient_data_analysis(self, agent):
        """Test patient data analysis task."""
        task = Task(
            id="test_patient_1",
            description="Analyze patient data",
            parameters={"task_type": "analyze_patient_data", "patient_id": "P123"},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_medical_research(self, agent):
        """Test medical research task."""
        task = Task(
            id="test_research_1",
            description="Medical research",
            parameters={"task_type": "medical_research", "topic": "diabetes"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_clinical_trial_analysis(self, agent):
        """Test clinical trial analysis task."""
        task = Task(
            id="test_trial_1",
            description="Clinical trial analysis",
            parameters={"task_type": "clinical_trial_analysis", "trial_id": "CT001"},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_epidemiology_study(self, agent):
        """Test epidemiology study task."""
        task = Task(
            id="test_epi_1",
            description="Epidemiology study",
            parameters={"task_type": "epidemiology_study", "disease": "influenza"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_personalized_medicine(self, agent):
        """Test personalized medicine task."""
        task = Task(
            id="test_personal_1",
            description="Personalized medicine",
            parameters={"task_type": "personalized_medicine", "patient_id": "P456"},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_health_monitoring(self, agent):
        """Test health monitoring task."""
        task = Task(
            id="test_monitor_1",
            description="Health monitoring",
            parameters={"task_type": "health_monitoring", "patient_id": "P789"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_unknown_task_type(self, agent):
        """Test handling of unknown task type."""
        task = Task(
            id="test_unknown_1",
            description="Unknown task",
            parameters={"task_type": "unknown_type"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        # VITA returns success with error in result for unknown types
        assert "error" in response.result
    
    @pytest.mark.asyncio
    async def test_get_stats(self, agent):
        """Test getting agent statistics."""
        stats = await agent.get_stats()
        assert stats is not None
        assert "specialization" in stats
        assert stats["specialization"] == "medical"


class TestAresAgent:
    """Test suite for ARES Agent (Strategic Planning)."""
    
    @pytest.fixture
    def agent(self):
        """Create ARES agent instance."""
        return AresAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "ares"
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """Test strategic planning task execution."""
        task = Task(
            id="test_task",
            description="Create strategic plan",
            parameters={"objectives": ["Increase efficiency"], "task_type": "create_strategic_plan"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'status')

    @pytest.mark.asyncio
    async def test_execute_optimize_resources(self, agent):
        """Test resource optimization task."""
        task = Task(
            id="test_opt_res_1",
            description="Optimize resources",
            parameters={
                "task_type": "optimize_resources",
                "resources": {
                    "personnel": [{"id": "p1", "skills": ["analysis"], "availability": 0.8}],
                    "equipment": [{"id": "e1", "type": "computer", "utilization": 0.5}],
                    "budget": {"total": 100000, "allocated": 60000}
                }
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_assess_risk(self, agent):
        """Test risk assessment task."""
        task = Task(
            id="test_risk_1",
            description="Assess project risk",
            parameters={
                "task_type": "assess_risk",
                "project_details": {
                    "name": "Test Project",
                    "timeline": "6 months",
                    "budget": 500000
                },
                "risk_factors": ["market_volatility", "resource_availability"]
            },
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_analyze_performance(self, agent):
        """Test performance analysis task."""
        task = Task(
            id="test_perf_1",
            description="Analyze performance",
            parameters={
                "task_type": "analyze_performance",
                "metrics": ["revenue", "efficiency", "customer_satisfaction"],
                "time_period": "Q1 2024"
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_optimize_supply_chain(self, agent):
        """Test supply chain optimization task."""
        task = Task(
            id="test_supply_1",
            description="Optimize supply chain",
            parameters={
                "task_type": "optimize_supply_chain",
                "supply_chain": {
                    "suppliers": [{"id": "s1", "reliability": 0.9, "cost": 100}],
                    "distribution_centers": [{"id": "d1", "capacity": 1000}],
                    "demand_forecast": {"product_a": 500, "product_b": 300}
                }
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_decision_support(self, agent):
        """Test decision support task."""
        task = Task(
            id="test_decision_1",
            description="Provide decision support",
            parameters={
                "task_type": "decision_support",
                "decision_context": {
                    "type": "investment",
                    "options": ["option_a", "option_b", "option_c"],
                    "criteria": ["roi", "risk", "timeline"]
                }
            },
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_business_intelligence(self, agent):
        """Test business intelligence task."""
        task = Task(
            id="test_bi_1",
            description="Generate business intelligence",
            parameters={
                "task_type": "business_intelligence",
                "data_sources": ["sales", "marketing", "operations"],
                "analysis_type": "trend_analysis"
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_forecast_demand(self, agent):
        """Test demand forecasting task."""
        task = Task(
            id="test_forecast_1",
            description="Forecast demand",
            parameters={
                "task_type": "forecast_demand",
                "historical_data": {
                    "product_a": [100, 120, 115, 130, 125],
                    "product_b": [50, 55, 60, 58, 62]
                },
                "forecast_period": "3_months"
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_unknown_task_type(self, agent):
        """Test unknown task type handling."""
        task = Task(
            id="test_unknown_1",
            description="Unknown task",
            parameters={"task_type": "unknown_type"},
            priority=TaskPriority.LOW
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert "error" in response.result

    @pytest.mark.asyncio
    async def test_validate_task_success(self, agent):
        """Test task validation with valid task type."""
        task = Task(
            id="test_validate_1",
            description="Valid task",
            parameters={"task_type": "create_strategic_plan"},
            priority=TaskPriority.MEDIUM
        )
        is_valid = await agent.validate_task(task)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_task_invalid(self, agent):
        """Test task validation with invalid task type."""
        task = Task(
            id="test_validate_2",
            description="Invalid task",
            parameters={"task_type": "invalid_type"},
            priority=TaskPriority.MEDIUM
        )
        is_valid = await agent.validate_task(task)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_optimization_methods(self, agent):
        """Test optimization methods are initialized."""
        assert agent.optimization_methods is not None
        assert len(agent.optimization_methods) > 0

    @pytest.mark.asyncio
    async def test_get_stats(self, agent):
        """Test get_stats method."""
        stats = await agent.get_stats()
        assert stats is not None
        assert "optimization_methods" in stats
        assert "specialization" in stats


class TestLEXCoreAgent:
    """Test suite for LEX-Core Agent (Legal & Compliance)."""
    
    @pytest.fixture
    def agent(self):
        """Create LEX-Core agent instance."""
        return LEXCoreAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "lex_core"
    
    @pytest.mark.asyncio
    async def test_execute_task(self, agent):
        """Test legal analysis task execution."""
        task = Task(
            id="test_task",
            description="Analyze legal document",
            parameters={"document_type": "contract", "content": "sample text", "task_type": "legal_document_analysis"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'status')

    @pytest.mark.asyncio
    async def test_execute_compliance_assessment(self, agent):
        """Test compliance assessment task."""
        task = Task(
            id="test_compliance_1",
            description="Assess compliance",
            parameters={
                "task_type": "compliance_assessment",
                "framework": "GDPR",
                "organization_data": {
                    "data_processing_activities": ["collection", "storage"],
                    "data_subjects": ["customers", "employees"]
                }
            },
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_contract_review(self, agent):
        """Test contract review task."""
        task = Task(
            id="test_contract_1",
            description="Review contract",
            parameters={
                "task_type": "contract_review",
                "contract_type": "service_agreement",
                "parties": ["Company A", "Company B"],
                "key_terms": ["payment", "termination", "liability"]
            },
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_regulatory_interpretation(self, agent):
        """Test regulatory interpretation task."""
        task = Task(
            id="test_regulatory_1",
            description="Interpret regulations",
            parameters={
                "task_type": "regulatory_interpretation",
                "regulation": "SOX",
                "query": "What are the key compliance requirements?",
                "industry": "financial_services"
            },
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_risk_assessment(self, agent):
        """Test legal risk assessment task."""
        task = Task(
            id="test_legal_risk_1",
            description="Assess legal risks",
            parameters={
                "task_type": "risk_assessment",
                "business_activity": "merger_acquisition",
                "jurisdiction": "US",
                "risk_factors": ["regulatory_approval", "antitrust"]
            },
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_policy_generation(self, agent):
        """Test policy generation task."""
        task = Task(
            id="test_policy_1",
            description="Generate policy",
            parameters={
                "task_type": "policy_generation",
                "policy_type": "data_privacy",
                "organization": "TechCorp",
                "scope": ["employee_data", "customer_data"]
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_audit_preparation(self, agent):
        """Test audit preparation task."""
        task = Task(
            id="test_audit_1",
            description="Prepare for audit",
            parameters={
                "task_type": "audit_preparation",
                "audit_type": "financial",
                "period": "Q1 2024",
                "requirements": ["documentation", "controls_evidence"]
            },
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_intellectual_property_analysis(self, agent):
        """Test IP analysis task."""
        task = Task(
            id="test_ip_1",
            description="Analyze intellectual property",
            parameters={
                "task_type": "intellectual_property_analysis",
                "ip_type": "patent",
                "invention_description": "AI-powered data processing system",
                "prior_art": ["existing_patent_1", "existing_patent_2"]
            },
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')

    @pytest.mark.asyncio
    async def test_execute_unknown_task_type(self, agent):
        """Test unknown task type handling."""
        task = Task(
            id="test_unknown_legal_1",
            description="Unknown task",
            parameters={"task_type": "unknown_legal_type"},
            priority=TaskPriority.LOW
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert response.error is not None or "error" in str(response.result).lower()

    @pytest.mark.asyncio
    async def test_legal_frameworks_initialized(self, agent):
        """Test legal frameworks are initialized."""
        assert agent.legal_frameworks is not None
        assert len(agent.legal_frameworks) > 0


class TestLUDUSAgent:
    """Test suite for LUDUS Agent (Simulation & Gaming)."""
    
    @pytest.fixture
    def agent(self):
        """Create LUDUS agent instance."""
        return LUDUSAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "ludus"
        assert hasattr(agent, 'active_simulations')
        assert hasattr(agent, 'metrics')
    
    @pytest.mark.asyncio
    async def test_execute_physics_simulation(self, agent):
        """Test physics simulation task."""
        task = Task(
            id="test_physics_1",
            description="Run physics simulation",
            parameters={"simulation_type": "physics", "scenario": "projectile", "task_type": "physics_simulation"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert response.agent_id == "ludus"
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_economic_modeling(self, agent):
        """Test economic modeling task."""
        task = Task(
            id="test_econ_1",
            description="Run economic model",
            parameters={"task_type": "economic_modeling", "model_type": "market"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_game_mechanics(self, agent):
        """Test game mechanics design task."""
        task = Task(
            id="test_game_1",
            description="Design game mechanics",
            parameters={"task_type": "game_mechanics_design", "game_type": "strategy"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_scenario_planning(self, agent):
        """Test scenario planning task."""
        task = Task(
            id="test_scenario_1",
            description="Plan scenario",
            parameters={"task_type": "scenario_planning", "domain": "business"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_virtual_prototype(self, agent):
        """Test virtual prototype creation task."""
        task = Task(
            id="test_proto_1",
            description="Create virtual prototype",
            parameters={"task_type": "virtual_prototyping", "prototype_type": "product"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_interactive_simulation(self, agent):
        """Test interactive simulation task."""
        task = Task(
            id="test_interactive_1",
            description="Run interactive simulation",
            parameters={"task_type": "interactive_simulation", "simulation_name": "test_sim"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_educational_game(self, agent):
        """Test educational game creation task."""
        task = Task(
            id="test_edu_1",
            description="Create educational game",
            parameters={"task_type": "educational_game", "subject": "math"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_strategic_war_game(self, agent):
        """Test strategic war game task."""
        task = Task(
            id="test_wargame_1",
            description="Run strategic war game",
            parameters={"task_type": "strategic_war_game", "scenario": "conflict"},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_unknown_task_type(self, agent):
        """Test handling of unknown task type."""
        from src.agents.base_agent import AgentStatus
        task = Task(
            id="test_unknown_1",
            description="Unknown task",
            parameters={"task_type": "unknown_type"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert response.status == AgentStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_validate_task_success(self, agent):
        """Test task validation with valid result."""
        task = Task(
            id="test_validate_1",
            description="Test validation",
            parameters={"task_type": "physics_simulation"},
            priority=TaskPriority.MEDIUM
        )
        result = {"status": "success", "simulation_results": {}}
        is_valid = await agent.validate_task(task, result)
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, agent):
        """Test that metrics are tracked correctly."""
        initial_received = agent.metrics.tasks_received
        initial_completed = agent.metrics.tasks_completed
        
        task = Task(
            id="test_metrics_1",
            description="Test metrics",
            parameters={"task_type": "physics_simulation"},
            priority=TaskPriority.MEDIUM
        )
        await agent.execute_task(task)
        
        assert agent.metrics.tasks_received == initial_received + 1
        assert agent.metrics.tasks_completed == initial_completed + 1


class TestARGUSAgent:
    """Test suite for ARGUS Agent (Monitoring & Analytics)."""
    
    @pytest.fixture
    def agent(self):
        """Create ARGUS agent instance."""
        return ARGUSAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.agent_id == "argus"
        assert hasattr(agent, 'metrics_database')
        assert hasattr(agent, 'task_history')
    
    @pytest.mark.asyncio
    async def test_execute_real_time_monitoring(self, agent):
        """Test real-time monitoring task."""
        task = Task(
            id="test_monitor_1",
            description="Monitor system",
            parameters={"scope": "system", "metrics": ["cpu_usage", "memory_usage"], "task_type": "real_time_monitoring"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert response.agent_id == "argus"
        assert response.task_id == "test_monitor_1"
    
    @pytest.mark.asyncio
    async def test_execute_performance_analytics(self, agent):
        """Test performance analytics task."""
        task = Task(
            id="test_perf_1",
            description="Analyze performance",
            parameters={"task_type": "performance_analytics", "time_range": "1h"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_log_analysis(self, agent):
        """Test log analysis task."""
        task = Task(
            id="test_log_1",
            description="Analyze logs",
            parameters={"task_type": "log_analysis", "log_source": "application"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_alert_management(self, agent):
        """Test alert management task."""
        task = Task(
            id="test_alert_1",
            description="Manage alerts",
            parameters={"task_type": "alert_management", "action": "list"},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_trend_analysis(self, agent):
        """Test trend analysis task."""
        task = Task(
            id="test_trend_1",
            description="Analyze trends",
            parameters={"task_type": "trend_analysis", "metric": "cpu_usage"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_anomaly_detection(self, agent):
        """Test anomaly detection task."""
        task = Task(
            id="test_anomaly_1",
            description="Detect anomalies",
            parameters={"task_type": "anomaly_detection", "sensitivity": "high"},
            priority=TaskPriority.HIGH
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_dashboard_generation(self, agent):
        """Test dashboard generation task."""
        task = Task(
            id="test_dashboard_1",
            description="Generate dashboard",
            parameters={"task_type": "dashboard_generation", "dashboard_type": "system"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_report_generation(self, agent):
        """Test report generation task."""
        task = Task(
            id="test_report_1",
            description="Generate report",
            parameters={"task_type": "report_generation", "report_type": "daily"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert hasattr(response, 'result')
    
    @pytest.mark.asyncio
    async def test_execute_unknown_task_type(self, agent):
        """Test handling of unknown task type."""
        from src.agents.base_agent import AgentStatus
        task = Task(
            id="test_unknown_1",
            description="Unknown task",
            parameters={"task_type": "unknown_type"},
            priority=TaskPriority.MEDIUM
        )
        response = await agent.execute_task(task)
        assert response is not None
        assert response.status == AgentStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_validate_task_success(self, agent):
        """Test task validation with valid result."""
        task = Task(
            id="test_validate_1",
            description="Test validation",
            parameters={"task_type": "real_time_monitoring"},
            priority=TaskPriority.MEDIUM
        )
        result = {"status": "success", "monitoring_results": {}}
        is_valid = await agent.validate_task(task, result)
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, agent):
        """Test that metrics are tracked correctly."""
        initial_received = agent.metrics.tasks_received
        initial_completed = agent.metrics.tasks_completed
        
        task = Task(
            id="test_metrics_1",
            description="Test metrics",
            parameters={"task_type": "real_time_monitoring"},
            priority=TaskPriority.MEDIUM
        )
        await agent.execute_task(task)
        
        assert agent.metrics.tasks_received == initial_received + 1
        assert agent.metrics.tasks_completed == initial_completed + 1
    
    @pytest.mark.asyncio
    async def test_task_history_tracking(self, agent):
        """Test that failed tasks are recorded in history."""
        task = Task(
            id="test_history_1",
            description="Test history",
            parameters={"task_type": "unknown_type"},
            priority=TaskPriority.MEDIUM
        )
        await agent.execute_task(task)
        
        # Task should be recorded in history due to error
        assert "test_history_1" in agent.task_history


if __name__ == "__main__":
    pytest.main([__file__, "-v"])