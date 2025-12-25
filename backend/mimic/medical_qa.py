"""
Medical Q&A Engine using MIMIC-IV knowledge
"""

from loguru import logger
from db.database import SessionLocal
from db.models import MedicalKnowledge
from typing import Optional, List

class MedicalQAEngine:
    """Answer medical questions using MIMIC-IV knowledge base"""

    def __init__(self):
        logger.info("Medical Q&A Engine initialized")
    
    def searchknowledge(self, query: str) -> Optional[str]:
        """
        Search medical knowledge base for relevant information
        
        Args:
            query: User's medical question
            
        Returns:
            str: Answer from knowledge base or None
        """
        try:
            db = SessionLocal()
            querylower = query.lower()
            
            # Search for matching terms
            results = db.query(MedicalKnowledge).filter(
                MedicalKnowledge.term.ilike(f"%{query}%") |
                MedicalKnowledge.description.ilike(f"%{query}%") |
                MedicalKnowledge.commonsymptoms.ilike(f"%{query}%")
            ).limit(3).all()
            
            db.close()
            
            if results:
                response = "Based on our medical database:\n\n"
                for result in results:
                    response += f"• {result.term} ({result.category})\n"
                    response += f"  {result.description}\n"
                    if result.commonsymptoms:
                        response += f"  Symptoms: {result.commonsymptoms}\n"
                    if result.severity:
                        response += f"  Severity: {result.severity}\n"
                    response += "\n"
                
                response += "\n⚠️ This is general information. Please consult with a doctor for personalized medical advice."
                return response
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching medical knowledge: {e}")
            return None
    
    def getemergencyinfo(self, condition: str) -> Optional[str]:
        """Get emergency information for a condition"""
        try:
            db = SessionLocal()
            
            result = db.query(MedicalKnowledge).filter(
                MedicalKnowledge.term.ilike(f"%{condition}%"),
                MedicalKnowledge.severity == "emergency"
            ).first()
            
            db.close()
            
            if result:
                return f"🚨 EMERGENCY: {result.term}\n{result.description}\nCall 911 immediately!"
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting emergency info: {e}")
            return None
    
    def getmedicationinfo(self, medication: str) -> Optional[str]:
        """Get information about a medication"""
        try:
            db = SessionLocal()
            
            result = db.query(MedicalKnowledge).filter(
                MedicalKnowledge.category == "medication",
                MedicalKnowledge.term.ilike(f"%{medication}%")
            ).first()
            
            db.close()
            
            if result:
                return f"{result.term}\n{result.description}\n{result.commonsymptoms}"
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting medication info: {e}")
            return None