from loguru import logger
from typing import Dict, List

class MedicalIntentClassifier:
    """Classify patient intents for medical receptionist"""
    
    def init(self):
        self.intentkeywords = {
            "emergency": [
                "emergency", "urgent", "chest pain", "heart attack", "stroke",
                "can't breathe", "bleeding", "unconscious", "seizure", "911",
                "ambulance", "severe pain", "overdose", "choking", "allergic reaction"
            ],
            "appointmentbooking": [
                "book", "schedule", "appointment", "make appointment", "see doctor",
                "visit", "consultation", "checkup", "reserve", "available"
            ],
            "appointmentinquiry": [
                "when is my appointment", "next appointment", "upcoming appointment",
                "check appointment", "appointment time", "what time", "when do I"
            ],
            "appointmentcancel": [
                "cancel", "reschedule", "change appointment", "move appointment",
                "different time", "different day"
            ],
            "medicalquestion": [
                "what is", "how do I", "should I", "is it normal", "symptoms",
                "medication", "treatment", "diagnosis", "condition", "disease"
            ],
            "prescriptionrefill": [
                "refill", "prescription", "medication", "pharmacy", "renew"
            ],
            "testresults": [
                "results", "lab results", "test results", "blood work", "x-ray"
            ],
            "billing": [
                "bill", "payment", "insurance", "cost", "charge", "invoice", "balance"
            ],
            "generalinquiry": [
                "hours", "location", "address", "phone", "contact", "directions"
            ],
            "greeting": [
                "hello", "hi", "hey", "good morning", "good afternoon", "good evening"
            ]
        }
    
    def classify(self, text: str) -> str:
        """
        Classify intent from user text
        
        Args:
            text: User input text
            
        Returns:
            str: Detected intent
        """
        textlower = text.lower()
        
        # Check for emergency first (highest priority)
        for keyword in self.intentkeywords["emergency"]:
            if keyword in textlower:
                logger.warning(f"EMERGENCY DETECTED: {text}")
                return "emergency"
        
        # Check other intents
        intentscores = {}
        for intent, keywords in self.intentkeywords.items():
            if intent == "emergency":
                continue
            score = sum(1 for keyword in keywords if keyword in textlower)
            if score > 0:
                intentscores[intent] = score
        
        if intentscores:
            detectedintent = max(intentscores, key=intentscores.get)
            logger.info(f"Intent detected: {detectedintent} (score: {intentscores[detectedintent]})")
            return detectedintent
        
        # Default to general inquiry
        return "generalinquiry"