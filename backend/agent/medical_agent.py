import json
import random
from loguru import logger
from agent.intentclassifier import MedicalIntentClassifier
from agent.emergencydetector import EmergencyDetector
from agent.knowledgebase import MedicalKnowledgeBase
from db.database import SessionLocal
from db.models import Patient, Doctor, Appointment, Call
from datetime import datetime, date, time, timedelta
import config

try:
    import ollama
    OLLAMAAVAILABLE = True
except ImportError:
    OLLAMAAVAILABLE = False
    logger.warning("Ollama not available, using rule-based responses")

class MedicalReceptionistAgent:
    """AI Medical Receptionist Agent"""
    
    def init(self):
        self.intentclassifier = MedicalIntentClassifier()
        self.emergencydetector = EmergencyDetector()
        self.knowledgebase = MedicalKnowledgeBase()
        self.conversationstate = {}
        
        if OLLAMAAVAILABLE and config.config.LLMPROVIDER == "ollama":
            self.usellm = True
            logger.info(f"Medical Agent initialized with LLM: {config.config.LLMMODEL}")
        else:
            self.usellm = False
            logger.info("Medical Agent initialized with rule-based system")
    
    def getgreeting(self) -> str:
        """Get varied, professional greeting"""
        greetings = [
            f"Good day! Thank you for calling {config.config.CLINICNAME}. This is your AI receptionist. How may I help you?",
            f"Hello! Welcome to {config.config.CLINICNAME}. I'm here to assist you. What can I do for you today?",
            f"Thank you for calling {config.config.CLINICNAME}. How can I help you today?",
            f"Hi there! You've reached {config.config.CLINICNAME}. How may I assist you?",
        ]
        return random.choice(greetings)
    
    async def processinput(self, userinput: str, conversationhistory: list, callid: str = None) -> str:
        """Process patient input with medical intelligence"""
        try:
            if callid is None:
                callid = "websession"
            
            # PRIORITY 1: Check for emergency
            isemergency, severity, emergencyadvice = self.emergencydetector.detectemergency(userinput)
            if isemergency:
                logger.critical(f"[Call {callid}] EMERGENCY: {severity}")
                protocol = self.emergencydetector.getemergencyprotocol(severity)
                return f"{emergencyadvice}\n\n{protocol}"
            
            # Classify intent
            intent = self.intentclassifier.classify(userinput)
            logger.info(f"[Call {callid}] Intent: {intent}")
            
            # Initialize conversation state
            if callid not in self.conversationstate:
                self.conversationstate[callid] = {
                    "intent": intent,
                    "patientid": None,
                    "patientname": None,
                    "verified": False,
                    "specialkey": None,
                    "awaitingname": False,
                    "awaitingkey": False,
                    "awaitingreason": False,
                    "appointmentreason": None,
                    "retrycount": 0
                }
            else:
                self.conversationstate[callid]["intent"] = intent
            
            state = self.conversationstate[callid]
            
            # Extract patient name if mentioned
            patientname = self.extractpatientname(userinput, state)
            if patientname:
                state["patientname"] = patientname
                state["awaitingname"] = False
            
            # Extract special key if mentioned
            specialkey = self.extractspecialkey(userinput)
            if specialkey:
                patient = self.verifypatientbykey(patientname or state.get("patientname"), specialkey)
                if patient:
                    state["patientid"] = patient.id
                    state["patientname"] = patient.name
                    state["specialkey"] = specialkey
                    state["verified"] = True
                    state["awaitingkey"] = False
            
            # Route to intent handlers
            if intent == "appointmentbooking":
                return await self.handleappointmentbooking(userinput, callid, conversationhistory)
            elif intent == "appointmentinquiry":
                return await self.handleappointmentinquiry(userinput, callid, conversationhistory)
            elif intent == "appointmentcancel":
                return await self.handleappointmentcancel(userinput, callid, conversationhistory)
            elif intent == "medicalquestion":
                return await self.handlemedicalquestion(userinput, callid, conversationhistory)
            elif intent == "prescriptionrefill":
                return await self.handleprescriptionrefill(userinput, callid, conversationhistory)
            elif intent == "testresults":
                return await self.handletestresults(userinput, callid, conversationhistory)
            elif intent == "billing":
                return await self.handlebilling(userinput, callid, conversationhistory)
            elif intent == "generalinquiry":
                return await self.handlegeneralinquiry(userinput, callid, conversationhistory)
            elif intent == "greeting":
                return await self.getsmartresponse(userinput, conversationhistory, callid, None, intent)
            else:
                return await self.getsmartresponse(userinput, conversationhistory, callid, None, intent)
                
        except Exception as e:
            logger.error(f"[Call {callid}] Error: {e}")
            state = self.conversationstate.get(callid, {})
            state["retrycount"] = state.get("retrycount", 0) + 1
            
            if state["retrycount"] < 3:
                return "I apologize, could you please repeat that?"
            else:
                return "I'm having difficulty understanding. Let me transfer you to our staff. Please hold."
    
    async def handleappointmentbooking(self, userinput: str, callid: str, conversationhistory: list) -> str:
        """Handle appointment booking"""
        state = self.conversationstate[callid]
        
        # Step 1: Get patient name
        if not state.get("patientname"):
            if state.get("awaitingname"):
                patientname = self.extractpatientname(userinput, state)
                if patientname:
                    state["patientname"] = patientname
                    state["awaitingname"] = False
                    state["awaitingkey"] = True
                    return f"Thank you, {patientname}. For verification, could you please provide your special key?"
                else:
                    return "I didn't catch your name. Could you please say your full name?"
            else:
                state["awaitingname"] = True
                return "I'd be happy to help you schedule an appointment. May I have your full name, please?"
        
        # Step 2: Verify patient
        if not state.get("verified"):
            if state.get("awaitingkey"):
                specialkey = self.extractspecialkey(userinput)
                if specialkey:
                    patient = self.verifypatientbykey(state["patientname"], specialkey)
                    if patient:
                        state["patientid"] = patient.id
                        state["verified"] = True
                        state["awaitingkey"] = False
                        state["awaitingreason"] = True
                        return f"Thank you, {patient.name}. I've verified your identity. What is the reason for your visit?"
                    else:
                        return "I couldn't verify that information. Could you please provide your special key again?"
                else:
                    return "I need your special key for verification. What is it?"
            else:
                state["awaitingkey"] = True
                return "For security, I need to verify your identity. Could you provide your special key?"
        
        # Step 3: Get reason for visit
        if not state.get("appointmentreason"):
            if state.get("awaitingreason"):
                state["appointmentreason"] = userinput
                state["awaitingreason"] = False
                
                # Get available slots
                availableslots = self.getavailableslots()
                if availableslots:
                    slotstext = "\n".join([f"• {slot['date']} at {slot['time']} with {slot['doctor']}" for slot in availableslots[:3]])
                    return f"I have the following appointments available:\n{slotstext}\n\nWhich time works best for you?"
                else:
                    return "I apologize, but we don't have any available appointments in the next two weeks. Would you like me to add you to our waiting list?"
            else:
                state["awaitingreason"] = True
                return "What is the reason for your visit?"
        
        # Step 4: Book appointment
        appointment = self.createappointment(
            patientid=state["patientid"],
            reason=state["appointmentreason"],
            userinput=userinput
        )
        
        if appointment:
            return f"Perfect! I've scheduled your appointment for {appointment['date']} at {appointment['time']} with {appointment['doctor']}. You'll receive a confirmation. Is there anything else I can help you with?"
        else:
            return "I'm having trouble booking that appointment. Let me transfer you to our scheduling team."
    
    async def handleappointmentinquiry(self, userinput: str, callid: str, conversationhistory: list) -> str:
        """Handle appointment inquiry"""
        state = self.conversationstate[callid]
        
        if not state.get("patientname"):
            if state.get("awaitingname"):
                patientname = self.extractpatientname(userinput, state)
                if patientname:
                    state["patientname"] = patientname
                    state["awaitingname"] = False
                    state["awaitingkey"] = True
                    return f"Thank you, {patientname}. For verification, could you provide your special key?"
                else:
                    return "I didn't catch your name. What is your full name?"
            else:
                state["awaitingname"] = True
                return "I can help you check your appointment. May I have your name, please?"
        
        if not state.get("verified"):
            if state.get("awaitingkey"):
                specialkey = self.extractspecialkey(userinput)
                if specialkey:
                    patient = self.verifypatientbykey(state["patientname"], specialkey)
                    if patient:
                        state["patientid"] = patient.id
                        state["verified"] = True
                        
                        appointments = self.getpatientappointments(patient.id)
                        if appointments:
                            appttext = "\n".join([
                                f"• {appt['date']} at {appt['time']} with {appt['doctor']} - {appt['reason']}"
                                for appt in appointments
                            ])
                            return f"Here are your upcoming appointments:\n{appttext}\n\nIs there anything else I can help you with?"
                        else:
                            return "You don't have any upcoming appointments scheduled. Would you like to book one?"
                    else:
                        return "I couldn't verify that information. Could you provide your special key again?"
                else:
                    return "I need your special key for verification. What is it?"
            else:
                state["awaitingkey"] = True
                return "For security, I need your special key. What is it?"
        
        return "I'm having trouble accessing your appointments. Let me transfer you to our staff."
    
    async def handleappointmentcancel(self, userinput: str, callid: str, conversationhistory: list) -> str:
        """Handle appointment cancellation"""
        state = self.conversationstate[callid]
        
        if not state.get("verified"):
            if not state.get("patientname"):
                state["awaitingname"] = True
                return "I can help you cancel or reschedule. May I have your name?"
            else:
                state["awaitingkey"] = True
                return "For verification, I need your special key. What is it?"
        
        appointments = self.getpatientappointments(state["patientid"])
        if appointments:
            cancelled = self.cancelappointment(appointments[0]['id'])
            if cancelled:
                return f"I've cancelled your appointment on {appointments[0]['date']} at {appointments[0]['time']}. Would you like to reschedule?"
        
        return "You don't have any upcoming appointments to cancel."
    
    async def handlemedicalquestion(self, userinput: str, callid: str, conversationhistory: list) -> str:
        """Handle medical questions"""
        kbresponse = self.knowledgebase.searchmedicalknowledge(userinput)
        if kbresponse:
            return kbresponse
        
        if self.usellm:
            return await self.getsmartresponse(userinput, conversationhistory, callid, None, "medicalquestion")
        
        return "That's a great question. For specific medical advice, I recommend scheduling an appointment with one of our doctors. Would you like me to book one for you?"
    
    async def handleprescriptionrefill(self, userinput: str, callid: str, conversationhistory: list) -> str:
        """Handle prescription refill"""
        state = self.conversationstate[callid]
        
        if not state.get("verified"):
            state["awaitingname"] = True
            return "I can help with prescription refills. May I have your name for verification?"
        
        return f"I've noted your prescription refill request. Our pharmacy team will contact you within 24 hours. Is there anything else I can help you with?"
    
    async def handletestresults(self, userinput: str, callid: str, conversationhistory: list) -> str:
        """Handle test results"""
        return "For test results, I recommend calling our lab directly at +1-555-LABS or checking your patient portal. Our doctors will also call you if there's anything urgent. Is there anything else I can help with?"
    
    async def handlebilling(self, userinput: str, callid: str, conversationhistory: list) -> str:
        """Handle billing"""
        return "For billing questions, our billing department is available at +1-555-BILL, Monday through Friday, 9 AM to 5 PM. They can help with insurance, payments, and statements. Is there anything else I can assist you with?"
    
    async def handlegeneralinquiry(self, userinput: str, callid: str, conversationhistory: list) -> str:
        """Handle general inquiries"""
        if any(word in userinput.lower() for word in ["hours", "location", "address", "phone"]):
            return self.knowledgebase.getclinicinfo(userinput)
        
        return await self.getsmartresponse(userinput, conversationhistory, callid, None, "generalinquiry")
    
    async def getsmartresponse(self, userinput: str, conversationhistory: list, callid: str, patient: Patient = None, intent: str = None) -> str:
        """Get intelligent response using LLM"""
        if not self.usellm:
            return "I'm here to help! Could you tell me more about what you need?"
        
        try:
            contextparts = [
                f"You are a professional medical receptionist at {config.config.CLINICNAME}.",
                "You are empathetic, efficient, and prioritize patient safety.",
                "Keep responses concise (1-2 sentences) for phone conversations.",
                "Always maintain HIPAA compliance - never share patient information without verification.",
                self.knowledgebase.getcontext()
            ]
            
            if patient:
                contextparts.append(f"Patient: {patient.name}")
            if intent:
                contextparts.append(f"Intent: {intent}")
            
            systemmessage = " ".join(contextparts)
            messages = [{"role": "system", "content": systemmessage}]
            messages.extend(conversationhistory[-8:])
            messages.append({"role": "user", "content": userinput})
            
            response = ollama.chat(
                model=config.config.LLMMODEL,
                messages=messages,
                options={
                    "temperature": config.config.LLMTEMPERATURE,
                    "numpredict": config.config.LLMMAXTOKENS
                }
            )
            
            return response['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "I apologize, I'm having trouble right now. How else can I help you?"
    
    def extractpatientname(self, text: str, state: dict) -> str:
        """Extract patient name"""
        import re
        patterns = [
            r"(?:my name is|i'm|i am|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"^([A-Z][a-z]+\s+[A-Z][a-z]+)$",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).title()
        return None
    
    def extractspecialkey(self, text: str) -> str:
        """Extract special key"""
        import re
        patterns = [
            r'\b([A-Z]+\d{4})\b',
            r'(?:key is|key:|special key)\s*([A-Z]+\d{4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None
    
    def verifypatientbykey(self, name: str, specialkey: str) -> Patient:
        """Verify patient"""
        try:
            db = SessionLocal()
            patient = db.query(Patient).filter(
                Patient.name.ilike(f"%{name}%"),
                Patient.specialkey == specialkey.upper()
            ).first()
            db.close()
            return patient
        except Exception as e:
            logger.error(f"Error verifying patient: {e}")
            return None
    
    def getpatientappointments(self, patientid: int) -> list:
        """Get patient appointments"""
        try:
            db = SessionLocal()
            today = date.today()
            appointments = db.query(Appointment).filter(
                Appointment.patientid == patientid,
                Appointment.appointmentdate >= today,
                Appointment.status == "scheduled"
            ).orderby(Appointment.appointmentdate, Appointment.appointmenttime).all()
            
            result = []
            for appt in appointments:
                doctor = db.query(Doctor).filter(Doctor.id == appt.doctorid).first()
                result.append({
                    "id": appt.id,
                    "date": appt.appointmentdate.strftime("%A, %B %d, %Y"),
                    "time": appt.appointmenttime.strftime("%I:%M %p"),
                    "doctor": doctor.name if doctor else "Dr. Unknown",
                    "reason": appt.reason or "General visit"
                })
            
            db.close()
            return result
        except Exception as e:
            logger.error(f"Error getting appointments: {e}")
            return []
    
    def getavailableslots(self, daysahead: int = 14) -> list:
        """Get available slots"""
        try:
            db = SessionLocal()
            today = date.today()
            slots = []
            
            doctors = db.query(Doctor).all()
            
            for dayoffset in range(1, daysahead + 1):
                checkdate = today + timedelta(days=dayoffset)
                dayname = checkdate.strftime("%A")
                
                if dayname not in config.config.CLINICDAYS:
                    continue
                
                for doctor in doctors:
                    if dayname in doctor.availabledays:
                        for hour in range(9, 17):
                            for minute in [0, 30]:
                                slottime = time(hour, minute)
                                
                                existing = db.query(Appointment).filter(
                                    Appointment.doctorid == doctor.id,
                                    Appointment.appointmentdate == checkdate,
                                    Appointment.appointmenttime == slottime,
                                    Appointment.status == "scheduled"
                                ).first()
                                
                                if not existing:
                                    slots.append({
                                        "date": checkdate.strftime("%A, %B %d"),
                                        "time": slottime.strftime("%I:%M %p"),
                                        "doctor": doctor.name,
                                        "doctorid": doctor.id,
                                        "datetime": checkdate,
                                        "timeobj": slottime
                                    })
                                
                                if len(slots) >= 10:
                                    db.close()
                                    return slots
            
            db.close()
            return slots
        except Exception as e:
            logger.error(f"Error getting slots: {e}")
            return []
    
    def createappointment(self, patientid: int, reason: str, userinput: str) -> dict:
        """Create appointment"""
        try:
            db = SessionLocal()
            slots = self.getavailableslots()
            
            if not slots:
                db.close()
                return None
            
            slot = slots[0]
            
            appointment = Appointment(
                patientid=patientid,
                doctorid=slot["doctorid"],
                appointmentdate=slot["datetime"],
                appointmenttime=slot["timeobj"],
                reason=reason,
                status="scheduled"
            )
            
            db.add(appointment)
            db.commit()
            db.refresh(appointment)
            
            result = {
                "id": appointment.id,
                "date": slot["date"],
                "time": slot["time"],
                "doctor": slot["doctor"]
            }
            
            db.close()
            return result
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            return None
    
    def cancelappointment(self, appointmentid: int) -> bool:
        """Cancel appointment"""
        try:
            db = SessionLocal()
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if appointment:
                appointment.status = "cancelled"
                db.commit()
                db.close()
                return True
            db.close()
            return False
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return False