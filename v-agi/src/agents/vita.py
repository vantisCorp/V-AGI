"""
VITA Agent - Biological and Medical Analysis

Provides:
- Medical diagnosis support
- Drug interaction analysis
- Biological data analysis
- Patient health monitoring
- Medical research assistance
- Clinical trial analysis
- Epidemiological studies
- Personalized medicine recommendations
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
from loguru import logger

from agents.base_agent import BaseAgent, Task, AgentResponse, AgentCapabilities, TaskPriority, AgentStatus
from enum import Enum


class MedicalDomain(Enum):
    """Medical domains."""
    DIAGNOSTICS = "diagnostics"
    PHARMACOLOGY = "pharmacology"
    EPIDEMIOLOGY = "epidemiology"
    GENOMICS = "genomics"
    CLINICAL_TRIALS = "clinical_trials"
    PUBLIC_HEALTH = "public_health"
    RESEARCH = "research"


@dataclass
class MedicalCondition:
    """Medical condition record."""
    condition_id: str
    name: str
    icd_code: str
    symptoms: List[str]
    severity: str
    prevalence: float
    treatments: List[str]
    contraindications: List[str]
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert condition to dictionary."""
        return {
            "condition_id": self.condition_id,
            "name": self.name,
            "icd_code": self.icd_code,
            "symptoms": self.symptoms,
            "severity": self.severity,
            "prevalence": self.prevalence,
            "treatments": self.treatments,
            "contraindications": self.contraindications,
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class DrugInteraction:
    """Drug interaction record."""
    drug_1: str
    drug_2: str
    interaction_type: str
    severity: str
    description: str
    recommendation: str
    evidence_level: str


@dataclass
class PatientAnalysis:
    """Patient analysis result."""
    patient_id: str
    conditions: List[str]
    risk_factors: List[str]
    recommendations: List[str]
    follow_up_actions: List[str]
    urgency: str
    analysis_date: datetime = field(default_factory=datetime.utcnow)


class VitaAgent(BaseAgent):
    """
    VITA Agent - Biological and medical analysis specialist.
    
    Capabilities:
    - Medical diagnosis support
    - Drug interaction analysis
    - Biological data analysis
    - Patient health monitoring
    - Medical research assistance
    - Clinical trial analysis
    - Epidemiological studies
    - Personalized medicine
    """
    
    def __init__(self, agent_id: str = "vita"):
        """Initialize VITA agent."""
        capabilities = AgentCapabilities(
            name="VITA",
            description="Biological and medical analysis agent",
            skills=[
                "medical_diagnosis",
                "drug_interaction_analysis",
                "biological_data_analysis",
                "patient_monitoring",
                "medical_research",
                "clinical_trial_analysis",
                "epidemiology",
                "personalized_medicine"
            ],
            tools=[
                "medical_database",
                "drug_database",
                "genomic_analyzer",
                "biological_simulator"
            ],
            max_concurrent_tasks=5,
            specialization="medical"
        )
        
        super().__init__(
            agent_id=agent_id,
            capabilities=capabilities,
            clearance_level=3  # High clearance for medical data
        )
        
        # Medical conditions database (simplified)
        self.conditions_database = {
            "hypertension": MedicalCondition(
                condition_id="cond_001",
                name="Hypertension",
                icd_code="I10",
                symptoms=["headache", "dizziness", "blurred vision", "shortness of breath"],
                severity="moderate",
                prevalence=0.30,
                treatments=["ACE inhibitors", "ARBs", "calcium channel blockers", "diuretics"],
                contraindications=["NSAIDs", "decongestants"]
            ),
            "diabetes_type2": MedicalCondition(
                condition_id="cond_002",
                name="Type 2 Diabetes",
                icd_code="E11",
                symptoms=["increased thirst", "frequent urination", "fatigue", "blurred vision"],
                severity="moderate",
                prevalence=0.10,
                treatments=["metformin", "insulin", "lifestyle changes"],
                contraindications=["corticosteroids", "thiazide diuretics"]
            ),
            "asthma": MedicalCondition(
                condition_id="cond_003",
                name="Asthma",
                icd_code="J45",
                symptoms=["wheezing", "shortness of breath", "chest tightness", "coughing"],
                severity="variable",
                prevalence=0.08,
                treatments=["inhaled corticosteroids", "bronchodilators", "leukotriene modifiers"],
                contraindications=["beta-blockers", "aspirin in some patients"]
            )
        }
        
        # Drug interaction database (simplified)
        self.drug_interactions = {
            ("ace_inhibitors", "nsaids"): DrugInteraction(
                drug_1="ACE Inhibitors",
                drug_2="NSAIDs",
                interaction_type="pharmacodynamic",
                severity="moderate",
                description="NSAIDs may reduce the antihypertensive effect of ACE inhibitors and increase risk of kidney damage",
                recommendation="Monitor blood pressure and kidney function regularly",
                evidence_level="high"
            ),
            ("insulin", "beta_blockers"): DrugInteraction(
                drug_1="Insulin",
                drug_2="Beta Blockers",
                interaction_type="pharmacodynamic",
                severity="moderate",
                description="Beta blockers may mask hypoglycemia symptoms and delay glucose recovery",
                recommendation="Monitor blood glucose frequently and educate patient on hypoglycemia recognition",
                evidence_level="high"
            ),
            ("warfarin", "aspirin"): DrugInteraction(
                drug_1="Warfarin",
                drug_2="Aspirin",
                interaction_type="pharmacodynamic",
                severity="high",
                description="Increased risk of bleeding due to additive antiplatelet effects",
                recommendation="Use with caution, monitor INR and signs of bleeding",
                evidence_level="high"
            )
        }
        
        logger.info(f"VITA agent initialized: {agent_id}")
    
    async def validate_task(self, task: Task) -> bool:
        """
        Validate if this agent can handle the task.
        
        Args:
            task: Task to validate
            
        Returns:
            True if agent can handle the task
        """
        valid_task_types = [
            "analyze_symptoms",
            "check_drug_interactions",
            "analyze_patient_data",
            "medical_research",
            "clinical_trial_analysis",
            "epidemiology_study",
            "personalized_medicine",
            "health_monitoring"
        ]
        
        task_type = task.parameters.get("task_type", "")
        return task_type in valid_task_types
    
    async def execute_task(self, task: Task) -> AgentResponse:
        """
        Execute a medical analysis task.
        
        Args:
            task: Task to execute
            
        Returns:
            Agent response with medical results
        """
        start_time = datetime.utcnow()
        await self.set_status(AgentStatus.PROCESSING)
        await self.add_task(task.id)
        
        try:
            task_type = task.parameters.get("task_type", "")
            
            if task_type == "analyze_symptoms":
                result = await self._analyze_symptoms(task)
            elif task_type == "check_drug_interactions":
                result = await self._check_drug_interactions(task)
            elif task_type == "analyze_patient_data":
                result = await self._analyze_patient_data(task)
            elif task_type == "medical_research":
                result = await self._medical_research(task)
            elif task_type == "clinical_trial_analysis":
                result = await self._clinical_trial_analysis(task)
            elif task_type == "epidemiology_study":
                result = await self._epidemiology_study(task)
            elif task_type == "personalized_medicine":
                result = await self._personalized_medicine(task)
            elif task_type == "health_monitoring":
                result = await self._health_monitoring(task)
            else:
                result = {
                    "error": f"Unknown task type: {task_type}",
                    "status": "error"
                }
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            response = AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status="success",
                result=result,
                execution_time=execution_time,
                metadata={"task_type": task_type}
            )
            
            await self.set_status(AgentStatus.IDLE)
            await self.remove_task(task.id)
            self.record_response(response)
            
            return response
            
        except Exception as e:
            logger.error(f"VITA agent error: {e}")
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            response = AgentResponse(
                task_id=task.id,
                agent_id=self.agent_id,
                status="error",
                error=str(e),
                execution_time=execution_time
            )
            
            await self.set_status(AgentStatus.ERROR)
            await self.remove_task(task.id)
            self.record_response(response)
            
            return response
    
    async def _analyze_symptoms(self, task: Task) -> Dict[str, Any]:
        """
        Analyze patient symptoms.
        
        Args:
            task: Task with symptom parameters
            
        Returns:
            Symptom analysis results
        """
        symptoms = task.parameters.get("symptoms", [])
        patient_age = task.parameters.get("age", 50)
        patient_gender = task.parameters.get("gender", "unknown")
        medical_history = task.parameters.get("medical_history", [])
        
        # Match symptoms to conditions
        potential_conditions = []
        
        for condition_id, condition in self.conditions_database.items():
            matching_symptoms = sum(1 for symptom in symptoms if symptom.lower() in [s.lower() for s in condition.symptoms])
            
            if matching_symptoms > 0:
                match_score = matching_symptoms / len(condition.symptoms)
                potential_conditions.append({
                    "condition": condition.name,
                    "icd_code": condition.icd_code,
                    "match_score": match_score,
                    "matching_symptoms": matching_symptoms,
                    "total_symptoms": len(condition.symptoms),
                    "severity": condition.severity,
                    "prevalence": condition.prevalence
                })
        
        # Sort by match score
        potential_conditions.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Generate recommendations
        top_conditions = potential_conditions[:3]
        recommendations = []
        
        for condition_data in top_conditions:
            condition = next(c for c in self.conditions_database.values() if c.name == condition_data["condition"])
            recommendations.extend(condition.treatments[:2])
        
        return {
            "symptoms_analyzed": len(symptoms),
            "potential_conditions": potential_conditions[:5],
            "top_conditions": top_conditions,
            "recommendations": recommendations,
            "urgency": self._assess_urgency(top_conditions),
            "disclaimer": "This analysis is for informational purposes only and should not replace professional medical advice"
        }
    
    def _assess_urgency(self, conditions: List[Dict[str, Any]]) -> str:
        """Assess urgency based on conditions."""
        if not conditions:
            return "low"
        
        high_severity = sum(1 for c in conditions if c["severity"] == "high")
        
        if high_severity > 0:
            return "high"
        elif any(c["match_score"] > 0.7 for c in conditions):
            return "moderate"
        else:
            return "low"
    
    async def _check_drug_interactions(self, task: Task) -> Dict[str, Any]:
        """
        Check for drug interactions.
        
        Args:
            task: Task with drug parameters
            
        Returns:
            Drug interaction results
        """
        medications = task.parameters.get("medications", [])
        patient_conditions = task.parameters.get("conditions", [])
        
        interactions_found = []
        
        # Check for interactions between all pairs of medications
        for i, drug1 in enumerate(medications):
            for drug2 in medications[i+1:]:
                # Normalize drug names
                key1 = drug1.lower().replace(" ", "_")
                key2 = drug2.lower().replace(" ", "_")
                
                # Check both orderings
                interaction = self.drug_interactions.get((key1, key2)) or self.drug_interactions.get((key2, key1))
                
                if interaction:
                    interactions_found.append({
                        "drug_1": interaction.drug_1,
                        "drug_2": interaction.drug_2,
                        "interaction_type": interaction.interaction_type,
                        "severity": interaction.severity,
                        "description": interaction.description,
                        "recommendation": interaction.recommendation,
                        "evidence_level": interaction.evidence_level
                    })
        
        # Assess overall risk
        high_severity = sum(1 for i in interactions_found if i["severity"] == "high")
        moderate_severity = sum(1 for i in interactions_found if i["severity"] == "moderate")
        
        overall_risk = "low"
        if high_severity > 0:
            overall_risk = "high"
        elif moderate_severity > 0:
            overall_risk = "moderate"
        
        return {
            "medications_analyzed": medications,
            "interactions_found": len(interactions_found),
            "interactions": interactions_found,
            "overall_risk": overall_risk,
            "recommendations": self._generate_interaction_recommendations(interactions_found),
            "disclaimer": "Consult a healthcare professional before making any medication changes"
        }
    
    def _generate_interaction_recommendations(self, interactions: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on interactions."""
        recommendations = []
        
        high_severity = [i for i in interactions if i["severity"] == "high"]
        moderate_severity = [i for i in interactions if i["severity"] == "moderate"]
        
        if high_severity:
            recommendations.append("URGENT: Review high-severity interactions with healthcare provider")
            for interaction in high_severity:
                recommendations.append(interaction["recommendation"])
        
        if moderate_severity:
            recommendations.append("Monitor for adverse effects from moderate-severity interactions")
            for interaction in moderate_severity:
                recommendations.append(interaction["recommendation"])
        
        if not interactions:
            recommendations.append("No known drug interactions detected")
        
        return recommendations
    
    async def _analyze_patient_data(self, task: Task) -> Dict[str, Any]:
        """
        Analyze patient health data.
        
        Args:
            task: Task with patient data parameters
            
        Returns:
            Patient analysis results
        """
        patient_id = task.parameters.get("patient_id", "")
        vitals = task.parameters.get("vitals", {})
        lab_results = task.parameters.get("lab_results", {})
        conditions = task.parameters.get("conditions", [])
        medications = task.parameters.get("medications", [])
        
        # Analyze vitals
        vital_anomalies = self._analyze_vitals(vitals)
        
        # Analyze lab results
        lab_anomalies = self._analyze_lab_results(lab_results)
        
        # Assess overall health status
        health_status = self._assess_health_status(vital_anomalies, lab_anomalies)
        
        # Generate recommendations
        recommendations = self._generate_health_recommendations(
            vital_anomalies,
            lab_anomalies,
            conditions
        )
        
        analysis = PatientAnalysis(
            patient_id=patient_id,
            conditions=conditions,
            risk_factors=vital_anomalies + lab_anomalies,
            recommendations=recommendations,
            follow_up_actions=self._generate_follow_up_actions(health_status),
            urgency=health_status["urgency"]
        )
        
        return {
            "patient_id": analysis.patient_id,
            "conditions": analysis.conditions,
            "risk_factors": analysis.risk_factors,
            "recommendations": analysis.recommendations,
            "follow_up_actions": analysis.follow_up_actions,
            "urgency": analysis.urgency,
            "health_status": health_status,
            "analysis_date": analysis.analysis_date.isoformat(),
            "disclaimer": "This analysis is for informational purposes only"
        }
    
    def _analyze_vitals(self, vitals: Dict[str, Any]) -> List[str]:
        """Analyze vital signs for anomalies."""
        anomalies = []
        
        # Blood pressure
        if "blood_pressure_systolic" in vitals and "blood_pressure_diastolic" in vitals:
            systolic = vitals["blood_pressure_systolic"]
            diastolic = vitals["blood_pressure_diastolic"]
            
            if systolic > 140 or diastolic > 90:
                anomalies.append("Elevated blood pressure detected")
            elif systolic < 90 or diastolic < 60:
                anomalies.append("Low blood pressure detected")
        
        # Heart rate
        if "heart_rate" in vitals:
            heart_rate = vitals["heart_rate"]
            if heart_rate > 100:
                anomalies.append("Elevated heart rate detected")
            elif heart_rate < 60:
                anomalies.append("Low heart rate detected")
        
        # Temperature
        if "temperature" in vitals:
            temperature = vitals["temperature"]
            if temperature > 37.5:
                anomalies.append("Elevated temperature detected")
            elif temperature < 36.0:
                anomalies.append("Low temperature detected")
        
        # Oxygen saturation
        if "oxygen_saturation" in vitals:
            spo2 = vitals["oxygen_saturation"]
            if spo2 < 95:
                anomalies.append("Low oxygen saturation detected")
        
        return anomalies
    
    def _analyze_lab_results(self, lab_results: Dict[str, Any]) -> List[str]:
        """Analyze laboratory results for anomalies."""
        anomalies = []
        
        # Glucose
        if "glucose" in lab_results:
            glucose = lab_results["glucose"]
            if glucose > 126:
                anomalies.append("Elevated glucose levels detected")
            elif glucose < 70:
                anomalies.append("Low glucose levels detected")
        
        # Cholesterol
        if "cholesterol_total" in lab_results:
            total = lab_results["cholesterol_total"]
            if total > 200:
                anomalies.append("Elevated cholesterol detected")
        
        # Hemoglobin
        if "hemoglobin" in lab_results:
            hemoglobin = lab_results["hemoglobin"]
            if hemoglobin < 12:
                anomalies.append("Low hemoglobin detected (possible anemia)")
        
        return anomalies
    
    def _assess_health_status(self, vital_anomalies: List[str], lab_anomalies: List[str]) -> Dict[str, Any]:
        """Assess overall health status."""
        total_anomalies = len(vital_anomalies) + len(lab_anomalies)
        
        if total_anomalies == 0:
            status = "excellent"
            urgency = "low"
        elif total_anomalies <= 2:
            status = "good"
            urgency = "low"
        elif total_anomalies <= 4:
            status = "moderate"
            urgency = "moderate"
        else:
            status = "attention_required"
            urgency = "high"
        
        return {
            "status": status,
            "urgency": urgency,
            "vital_anomalies": len(vital_anomalies),
            "lab_anomalies": len(lab_anomalies),
            "total_anomalies": total_anomalies
        }
    
    def _generate_health_recommendations(
        self,
        vital_anomalies: List[str],
        lab_anomalies: List[str],
        conditions: List[str]
    ) -> List[str]:
        """Generate health recommendations."""
        recommendations = []
        
        if "Elevated blood pressure detected" in vital_anomalies:
            recommendations.append("Monitor blood pressure regularly")
            recommendations.append("Consider dietary sodium reduction")
            recommendations.append("Consult healthcare provider for evaluation")
        
        if "Elevated glucose levels detected" in lab_anomalies:
            recommendations.append("Monitor blood glucose levels")
            recommendations.append("Review diet and exercise routine")
            recommendations.append("Consider diabetes screening")
        
        if not vital_anomalies and not lab_anomalies:
            recommendations.append("Continue regular health monitoring")
            recommendations.append("Maintain healthy lifestyle")
            recommendations.append("Schedule routine check-ups")
        
        return recommendations
    
    def _generate_follow_up_actions(self, health_status: Dict[str, Any]) -> List[str]:
        """Generate follow-up actions."""
        actions = []
        
        if health_status["urgency"] == "high":
            actions.append("Schedule appointment with healthcare provider within 24 hours")
        elif health_status["urgency"] == "moderate":
            actions.append("Schedule appointment with healthcare provider within 1 week")
        else:
            actions.append("Schedule routine follow-up as recommended")
        
        actions.append("Continue monitoring vital signs")
        actions.append("Keep detailed health records")
        
        return actions
    
    async def _medical_research(self, task: Task) -> Dict[str, Any]:
        """
        Assist with medical research.
        
        Args:
            task: Task with research parameters
            
        Returns:
            Research assistance results
        """
        research_topic = task.parameters.get("topic", "")
        research_type = task.parameters.get("type", "literature_review")
        keywords = task.parameters.get("keywords", [])
        
        # Simulate research assistance (placeholder)
        # In production, query medical databases and analyze literature
        
        research_results = {
            "topic": research_topic,
            "research_type": research_type,
            "keywords": keywords,
            "findings": [
                {
                    "source": "Simulated Medical Journal 1",
                    "year": 2023,
                    "findings": f"Recent studies on {research_topic} show promising results",
                    "relevance": 0.85
                },
                {
                    "source": "Simulated Medical Journal 2",
                    "year": 2022,
                    "findings": f"Meta-analysis of {research_topic} research indicates significant correlation",
                    "relevance": 0.78
                }
            ],
            "summary": f"Current research on {research_topic} indicates growing interest in the field",
            "recommendations": [
                "Conduct systematic literature review",
                "Identify gaps in current knowledge",
                "Consider clinical trial design"
            ],
            "references_count": 2
        }
        
        return research_results
    
    async def _clinical_trial_analysis(self, task: Task) -> Dict[str, Any]:
        """
        Analyze clinical trial data.
        
        Args:
            task: Task with clinical trial parameters
            
        Returns:
            Clinical trial analysis results
        """
        trial_id = task.parameters.get("trial_id", "")
        trial_phase = task.parameters.get("phase", "unknown")
        outcomes = task.parameters.get("outcomes", {})
        
        # Simulate clinical trial analysis (placeholder)
        
        analysis = {
            "trial_id": trial_id,
            "phase": trial_phase,
            "sample_size": 1000,
            "treatment_group": {
                "size": 500,
                "response_rate": 0.75,
                "adverse_events": 50
            },
            "control_group": {
                "size": 500,
                "response_rate": 0.45,
                "adverse_events": 30
            },
            "statistical_significance": 0.01,
            "effect_size": 0.30,
            "conclusions": "Treatment shows statistically significant improvement over control",
            "recommendations": [
                "Proceed to next phase",
                "Monitor long-term effects",
                "Consider larger sample size for phase 3"
            ]
        }
        
        return analysis
    
    async def _epidemiology_study(self, task: Task) -> Dict[str, Any]:
        """
        Conduct epidemiological analysis.
        
        Args:
            task: Task with epidemiology parameters
            
        Returns:
            Epidemiology study results
        """
        disease = task.parameters.get("disease", "")
        population = task.parameters.get("population", {})
        time_period = task.parameters.get("time_period", "1 year")
        
        # Simulate epidemiology study (placeholder)
        
        study = {
            "disease": disease,
            "population_size": population.get("size", 1000000),
            "cases_reported": 5000,
            "incidence_rate": 0.005,
            "prevalence": 0.02,
            "mortality_rate": 0.001,
            "risk_factors": ["age", "comorbidities", "exposure"],
            "trends": "increasing",
            "predictions": {
                "next_quarter": "moderate increase expected",
                "next_year": "stable to slightly increasing"
            },
            "recommendations": [
                "Enhance surveillance",
                "Public awareness campaign",
                "Vaccination program consideration"
            ]
        }
        
        return study
    
    async def _personalized_medicine(self, task: Task) -> Dict[str, Any]:
        """
        Provide personalized medicine recommendations.
        
        Args:
            task: Task with personalized medicine parameters
            
        Returns:
            Personalized medicine recommendations
        """
        patient_id = task.parameters.get("patient_id", "")
        genetic_profile = task.parameters.get("genetic_profile", {})
        conditions = task.parameters.get("conditions", [])
        medications = task.parameters.get("medications", [])
        
        # Simulate personalized medicine analysis (placeholder)
        
        recommendations = {
            "patient_id": patient_id,
            "genetic_markers": list(genetic_profile.keys()),
            "pharmacogenomics": {
                "metabolizer_type": "intermediate",
                "drug_response_predictions": {
                    "standard_dose": "likely effective",
                    "adjusted_dose": "may require adjustment"
                }
            },
            "disease_risk": {
                "elevated_risk": ["condition_1"],
                "normal_risk": ["condition_2"]
            },
            "treatment_recommendations": [
                "Consider genetic testing for medication optimization",
                "Monitor treatment response closely",
                "Adjust dosage based on metabolizer type"
            ],
            "preventive_measures": [
                "Regular screening for elevated risk conditions",
                "Lifestyle modifications based on genetic profile"
            ],
            "disclaimer": "Personalized medicine recommendations should be reviewed by healthcare professionals"
        }
        
        return recommendations
    
    async def _health_monitoring(self, task: Task) -> Dict[str, Any]:
        """
        Monitor patient health trends.
        
        Args:
            task: Task with health monitoring parameters
            
        Returns:
            Health monitoring results
        """
        patient_id = task.parameters.get("patient_id", "")
        time_range = task.parameters.get("time_range", "30 days")
        metrics = task.parameters.get("metrics", [])
        
        # Simulate health monitoring (placeholder)
        
        monitoring_results = {
            "patient_id": patient_id,
            "time_range": time_range,
            "metrics_monitored": metrics,
            "trends": {
                "blood_pressure": "stable",
                "weight": "slight increase",
                "activity_level": "improving",
                "medication_adherence": "high"
            },
            "alerts": [
                "Weight gain of 2kg over the period",
                "Consider diet and exercise review"
            ],
            "recommendations": [
                "Continue current monitoring schedule",
                "Address weight gain with healthcare provider",
                "Maintain medication adherence"
            ],
            "next_review_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        return monitoring_results
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get VITA agent statistics.
        
        Returns:
            Dictionary containing statistics
        """
        return {
            "conditions_database_size": len(self.conditions_database),
            "drug_interactions_database_size": len(self.drug_interactions),
            "supported_domains": [d.value for d in MedicalDomain],
            "specialization": "medical",
            "capabilities": self.capabilities.skills
        }