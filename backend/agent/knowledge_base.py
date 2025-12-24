from loguru import logger
from db.database import SessionLocal
from db.models import MedicalKnowledge
import config

class MedicalKnowledgeBase:
    """Medical knowledge base for answering patient questions"""
    
    def init(self):
        self.clinicinfo = {
            "name": config.config.CLINICNAME,
            "hours": f"{config.config.CLINICHOURSSTART} - {config.config.CLINICHOURSEND}",
            "days": ", ".join(config.config.CLINICDAYS),
            "phone": "+1-555-CLINIC",
            "address": "123 Medical Plaza, Healthcare City, HC 12345"
        }
    
    def getgreeting(self) -> str:
        """Get greeting message"""
        return f"Thank you for calling {self.clinicinfo['name']}. How may I help you today?"
    
    def getclinicinfo(self, query: str) -> str:
        """Get clinic information"""
        querylower = query.lower()
        
        if "hours" in querylower or "open" in querylower:
            return f"Our clinic hours are {self.clinicinfo['hours']}, {self.clinicinfo['days']}."
        
        if "location" in querylower or "address" in querylower:
            return f"We're located at {self.clinicinfo['address']}."
        
        if "phone" in querylower or "contact" in querylower:
            return f"You can reach us at {self.clinicinfo['phone']}."
        
        return f"Our clinic is open {self.clinicinfo['hours']}, {self.clinicinfo['days']}. We're located at {self.clinicinfo['address']}."
    
    def searchmedicalknowledge(self, query: str) -> str:
        """Search medical knowledge base"""
        try:
            db = SessionLocal()
            querylower = query.lower()
            
            # Search for matching terms
            results = db.query(MedicalKnowledge).filter(
                MedicalKnowledge.term.ilike(f"%{query}%") |
                MedicalKnowledge.description.ilike(f"%{query}%")
            ).limit(3).all()
            
            db.close()
            
            if results:
                response = "Based on our medical database:\n\n"
                for result in results:
                    response += f"• {result.term}: {result.description}\n"
                response += "\nPlease consult with a doctor for personalized medical advice."
                return response
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching medical knowledge: {e}")
            return None
    
    def getcontext(self) -> str:
        """Get context for LLM"""
        return (
            f"You are a medical receptionist at {self.clinicinfo['name']}. "
            f"Clinic hours: {self.clinicinfo['hours']}, {self.clinicinfo['days']}. "
            f"Location: {self.clinic_info['address']}. "
            "You help patients schedule appointments, answer questions, and provide basic medical information. "
            "Always be empathetic, professional, and prioritize patient safety. "
            "For medical emergencies, immediately advise calling 911."
        )