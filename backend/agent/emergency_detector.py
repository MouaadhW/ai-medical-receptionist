from loguru import logger
from typing import Dict, Tuple
import config

class EmergencyDetector:
    """Detect medical emergencies and provide triage"""
    
    def init(self):
        self.emergencykeywords = config.config.EMERGENCYKEYWORDS
        
        self.severitylevels = {
            "critical": [
                "chest pain", "heart attack", "stroke", "can't breathe",
                "severe bleeding", "unconscious", "not breathing", "choking"
            ],
            "urgent": [
                "severe pain", "high fever", "vomiting blood", "seizure",
                "allergic reaction", "broken bone", "deep cut"
            ],
            "moderate": [
                "fever", "pain", "bleeding", "dizzy", "nausea", "rash"
            ]
        }
    
    def detectemergency(self, text: str) -> Tuple[bool, str, str]:
        """
        Detect if text contains emergency keywords
        
        Args:
            text: User input text
            
        Returns:
            Tuple[bool, str, str]: (isemergency, severity, advice)
        """
        textlower = text.lower()
        
        # Check critical emergencies
        for keyword in self.severitylevels["critical"]:
            if keyword in textlower:
                logger.critical(f"CRITICAL EMERGENCY DETECTED: {keyword}")
                return (
                    True,
                    "critical",
                    "This is a medical emergency. Please call 911 immediately or go to the nearest emergency room. Do not wait."
                )
        
        # Check urgent situations
        for keyword in self.severitylevels["urgent"]:
            if keyword in textlower:
                logger.warning(f"URGENT SITUATION DETECTED: {keyword}")
                return (
                    True,
                    "urgent",
                    "This requires immediate medical attention. Please go to the emergency room or urgent care center right away."
                )
        
        # Check moderate concerns
        for keyword in self.severitylevels["moderate"]:
            if keyword in textlower:
                logger.info(f"MODERATE CONCERN DETECTED: {keyword}")
                return (
                    False,
                    "moderate",
                    "I recommend scheduling an appointment with your doctor soon to address this concern."
                )
        
        return (False, "none", "")
    
    def getemergencyprotocol(self, severity: str) -> str:
        """Get emergency protocol based on severity"""
        protocols = {
            "critical": (
                "EMERGENCY PROTOCOL ACTIVATED:\n"
                "1. Call 911 immediately\n"
                "2. Do not drive yourself\n"
                "3. Stay on the line with 911\n"
                "4. If alone, unlock your door for paramedics"
            ),
            "urgent": (
                "URGENT CARE PROTOCOL:\n"
                "1. Go to nearest emergency room or urgent care\n"
                "2. Have someone drive you if possible\n"
                "3. Bring your insurance card and ID\n"
                "4. Call us when you arrive"
            ),
            "moderate": (
                "STANDARD CARE PROTOCOL:\n"
                "1. Schedule appointment within 24-48 hours\n"
                "2. Monitor symptoms\n"
                "3. Call back if symptoms worsen"
            )
        }
        return protocols.get(severity, "")