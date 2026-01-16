"""
AI Insights Service - Generate intelligent explanations and summaries
Uses the existing LLM (Llama 3.1) from the medical agent
"""

import os
from typing import Dict, List
import ollama
from config import config


class AIInsightsService:
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = config.LLMMODEL
        # Initialize client directly
        self.client = ollama.Client(host=self.ollama_host)

    def generate_bill_explanation(self, item_description: str, category: str, patient_context: str = "") -> str:
        """Generate AI explanation for a bill item"""
        prompt = f"""You are a helpful medical bill explainer. Explain this medical charge in simple, patient-friendly language.

Charge: {item_description}
Category: {category}
Patient Context: {patient_context if patient_context else 'General'}

Provide a brief 1-2 sentence explanation of:
1. What this charge is for
2. Why it might have been necessary

Keep it friendly, clear, and avoid medical jargon."""

        try:
            response = self.client.generate(model=self.model, prompt=prompt)
            return response.get('services', {}).get('response', response.get('response', '')).strip()
        except Exception as e:
            return f"This is a {category} charge for {item_description}."

    def generate_medical_event_summary(self, event_data: Dict) -> str:
        """Generate key takeaways from a medical event"""
        prompt = f"""Summarize this medical event in one clear sentence for the patient:

Event Type: {event_data.get('event_type', 'medical event')}
Title: {event_data.get('title', 'N/A')}
Description: {event_data.get('description', 'N/A')}
Date: {event_data.get('event_date', 'N/A')}

Create a patient-friendly key takeaway that explains what happened and why it matters."""

        try:
            response = self.client.generate(model=self.model, prompt=prompt)
            return response.get('response', '').strip()
        except Exception as e:
            return f"{event_data.get('title', 'Medical event')} on {event_data.get('event_date', 'this date')}."

    def generate_follow_up_recommendation(self, event_data: Dict) -> str:
        """Generate follow-up recommendation for a medical event"""
        prompt = f"""Based on this medical event, provide a brief follow-up recommendation:

Event: {event_data.get('title', 'N/A')}
Type: {event_data.get('event_type', 'N/A')}
Status: {event_data.get('status', 'N/A')}
Severity: {event_data.get('severity', 'N/A')}

Suggest what the patient should do next (e.g., schedule follow-up, monitor symptoms, etc.).
Keep it to 1-2 sentences."""

        try:
            response = self.client.generate(model=self.model, prompt=prompt)
            return response.get('response', '').strip()
        except Exception as e:
            if event_data.get('status') == 'follow_up_needed':
                return "Consider scheduling a follow-up appointment with your provider."
            return "Continue monitoring as advised by your healthcare provider."

    def predict_visit_cost(self, patient_history: List[Dict], visit_type: str) -> Dict:
        """
        Simple cost prediction based on historical data
        In a real system, this would use ML models trained on historical billing data
        """
        # Mock prediction for demonstration
        # In production, you'd analyze patient_history to find similar past visits
        
        base_costs = {
            "routine_checkup": {"min": 80, "max": 150, "avg": 115},
            "follow_up": {"min": 60, "max": 120, "avg": 90},
            "specialist": {"min": 150, "max": 300, "avg": 225},
            "emergency": {"min": 500, "max": 2000, "avg": 1250},
            "lab_work": {"min": 100, "max": 400, "avg": 250}
        }

        costs = base_costs.get(visit_type, {"min": 100, "max": 300, "avg": 200})
        
        # Add some variance based on patient history
        history_count = len(patient_history)
        if history_count > 5:
            # Slight increase for patients with more complex history            costs["min"] *= 1.1
            costs["max"] *= 1.15
            costs["avg"] *= 1.12

        breakdown = {
            "consultation": costs["avg"] * 0.4,
            "lab_tests": costs["avg"] * 0.3,
            "procedures": costs["avg"] * 0.2,
            "medications": costs["avg"] * 0.1
        }

        return {
            "min_cost": round(costs["min"], 2),
            "max_cost": round(costs["max"], 2),
            "avg_cost": round(costs["avg"], 2),
            "confidence": 0.75,  # Mock confidence score
            "breakdown": breakdown
        }

    def analyze_cost_vs_value(self, bill_data: Dict) -> Dict:
        """Calculate cost savings from MedPulse automation"""
        total = bill_data.get("total_amount", 0)
        
        # Estimate savings (mock calculation)
        # In real system, compare against industry averages
        traditional_cost = total * 1.35  # Assume 35% markup in traditional clinics
        ai_savings = traditional_cost - total
        time_saved_hours = 2.5  # Average time saved through automation
        
        return {
            "medpulse_cost": total,
            "traditional_cost": round(traditional_cost, 2),
            "money_saved": round(ai_savings, 2),
            "time_saved_hours": time_saved_hours,
            "efficiency_gains": [
                "No wait time for billing inquiries",
                "Instant insurance verification",
                "AI-powered cost explanations",
                "Automated appointment scheduling"
            ]
        }


# Singleton instance
ai_insights_service = AIInsightsService()
