import json
import random
from loguru import logger
from agent.intent_classifier import MedicalIntentClassifier
from agent.emergency_detector import EmergencyDetector
from agent.knowledge_base import MedicalKnowledgeBase
from db.database import SessionLocal
from db.models import Patient, Doctor, Appointment, Call, User, TempCall
from datetime import datetime, date, time, timedelta
import config
import re
from services.email_service import email_service

try:
    import ollama
    OLLAMAAVAILABLE = True
except ImportError:
    OLLAMAAVAILABLE = False
    logger.warning("Ollama not available, using rule-based responses")

class MedicalReceptionistAgent:
    """AI Medical Receptionist Agent"""

    def __init__(self):
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
        return "Hello! Welcome to AI Medical Receptionist. I am an AI assistant here to help you. How may I assist you today?"
        
    def _create_json_response(self, spoken_text: str, metadata: dict = None) -> str:
        """Create standardized JSON response"""
        if metadata is None:
            metadata = {}
        return json.dumps({
            "spoken_response": spoken_text,
            "metadata": metadata
        })

    
    async def processinput(self, userinput: str, conversationhistory: list, callid: str = None, user_context: dict = None) -> str:
        """Process patient input with medical intelligence"""
        print(f"DEBUG_AGENT: processinput received input='{userinput}', context={user_context}", flush=True)
        try:
            if callid is None:
                callid = "websession"
            
            # PRIORITY 1: Check for emergency
            isemergency, severity, emergencyadvice = self.emergencydetector.detectemergency(userinput)
            if isemergency:
                logger.critical(f"[Call {callid}] EMERGENCY: {severity}")
                protocol = self.emergencydetector.getemergencyprotocol(severity)
                return self._create_json_response(
                    f"{emergencyadvice}\n\n{protocol}",
                    {"is_emergency": True, "severity": severity}
                )
            
            # Classify intent
            intent = self.intentclassifier.classify(userinput)
            logger.info(f"[Call {callid}] Intent: {intent}")
            
            # Initialize conversation state
            # Check state
            logger.info(f"[Call {callid}] Processing input. State exists? {callid in self.conversationstate}")
            if callid in self.conversationstate:
                logger.info(f"[Call {callid}] Current State: {self.conversationstate[callid]}")

            if callid not in self.conversationstate:
                self.conversationstate[callid] = {
                    "intent": intent,
                    "patientid": None,
                    "patientname": None,
                    "phone": None,
                    "verified": False,
                    "otid": None,
                    "awaitingname": False,
                    "awaitingkey": False,
                    "awaitingreason": False,
                    "appointmentreason": None,
                    "retrycount": 0
                }
            else:
                self.conversationstate[callid]["intent"] = intent
            
            # Apply Context Overrides (CRITICAL FIX)
            if user_context:
                self.conversationstate[callid].update(user_context)
            
            state = self.conversationstate[callid]
            
            # Extract patient name if mentioned (only if not already set)
            patientname = self.extractpatientname(userinput, state)
            if patientname:
                state["patientname"] = patientname
                state["awaitingname"] = False
            
            # Extract OTID if mentioned
            otid = self.extractotid(userinput)
            if otid:
                user = self.verifyuserbyotid(otid)
                if user:
                    # Link to patient if exists
                    if user.patient_id:
                        state["patientid"] = user.patient_id
                        state["patientname"] = user.patient.name
                    else:
                        # User exists but no patient record? Use username or created temp
                        state["patientname"] = user.username
                    
                    state["otid"] = otid
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
                return self._create_json_response(
                    "I apologize, could you please repeat that?",
                    {"error": str(e), "retry": True}
                )
            else:
                return self._create_json_response(
                    "I'm having difficulty understanding. Let me transfer you to our staff. Please hold.",
                    {"error": str(e), "transfer": True}
                )
    
    async def handleappointmentbooking(self, userinput: str, callid: str, conversationhistory: list) -> str:
        """Handle appointment booking"""
        state = self.conversationstate[callid]
        
        # Auto-verify authenticated users
        if state.get("userid") and not state.get("verified"):
            logger.info(f"Auto-verifying authenticated user {state.get('patientname')}")
            state["verified"] = True
            state["awaitingkey"] = False
        
        # Step 1: Get patient name
        if not state.get("patientname"):
            if state.get("awaitingname"):
                patientname = self.extractpatientname(userinput, state)
                if patientname:
                    state["patientname"] = patientname
                    state["awaitingname"] = False
                    
                    # Check if OTID was also provided in the same message
                    otid_in_msg = self.extractotid(userinput)
                    if otid_in_msg:
                         user = self.verifyuserbyotid(otid_in_msg)
                         if user:
                            state["userid"] = user.id
                            if user.patient:
                                state["patientid"] = user.patient.id
                            state["verified"] = True
                            state["awaitingkey"] = False
                            # Skip to reason
                            state["awaitingreason"] = True
                            return self._create_json_response(
                                f"Thank you, {patientname}. I've verified your identity. What is the reason for your visit?",
                                {"intent": "booking", "step": "ask_reason", "verified": True}
                            )

                    state["awaitingkey"] = True
                    return self._create_json_response(
                        f"Thank you, {patientname}. For verification, could you please provide your 5-digit security code (OTID)?",
                        {"intent": "booking", "step": "verification"}
                    )
                else:
                    return self._create_json_response(
                        "I didn't catch your name. Could you please say your full name?",
                        {"intent": "booking", "step": "name_retry"}
                    )
            else:
                state["awaitingname"] = True
                # If not verified, mention verification early
                if not state.get("verified"):
                     return self._create_json_response(
                        "I'd be happy to help you schedule an appointment. For security, may I have your full name and 5-digit OTID?",
                        {"intent": "booking", "step": "ask_name_otid"}
                    )
                return self._create_json_response(
                    "I'd be happy to help you schedule an appointment. May I have your full name, please?",
                    {"intent": "booking", "step": "ask_name"}
                )
        
        # Step 2: Verify patient
        if not state.get("verified"):
            if state.get("awaitingkey"):
                otid = self.extractotid(userinput)
                if otid:
                    user = self.verifyuserbyotid(otid)
                    if user:
                        state["userid"] = user.id  # Store user ID for appointment linking
                        if user.patient:
                            state["patientid"] = user.patient.id
                            state["patientname"] = user.patient.name
                        state["verified"] = True
                        state["awaitingkey"] = False
                        state["awaitingreason"] = True
                        
                        return self._create_json_response(
                            f"Thank you, {state['patientname']}. Verification successful. What is the reason for your visit?",
                            {"intent": "booking", "step": "ask_reason", "verified": True}
                        )
                    else:
                        return self._create_json_response(
                            "I couldn't verify that code. Could you please provide your 5-digit OTID again?",
                            {"intent": "booking", "step": "verify_fail"}
                        )
                else:
                    return self._create_json_response(
                        "I need your 5-digit security code for verification. What is it?",
                        {"intent": "booking", "step": "ask_key"}
                    )
            else:
                state["awaitingkey"] = True
                return self._create_json_response(
                    "For security, I need to verify your identity. Could you provide your 5-digit OTID?",
                    {"intent": "booking", "step": "ask_key_init"}
                )
        
        # Step 3: Get reason for visit
        if not state.get("appointmentreason"):
            if state.get("awaitingreason"):
                state["appointmentreason"] = userinput
                state["awaitingreason"] = False
                state["awaitingdoctorpref"] = True # Move to next step
                
                return self._create_json_response(
                    "Do you have a specific doctor you would like to see, or would you like me to recommend one?",
                    {"intent": "booking", "step": "ask_doctor"}
                )
            else:
                 state["awaitingreason"] = True
                 return self._create_json_response(
                    "What is the reason for your visit?",
                    {"intent": "booking", "step": "ask_reason_retry"}
                )

        # Step 4: Get Doctor Preference
        if not state.get("selecteddoctorid"):
            if state.get("awaitingdoctorpref"):
                # Analyze preference
                selected_doc = self.find_doctor_by_preference(userinput, state.get("appointmentreason"))
                if selected_doc:
                    state["selecteddoctorid"] = selected_doc.id
                    state["selecteddoctorname"] = selected_doc.name
                    state["awaitingdoctorpref"] = False
                    
                    # Now show slots for THIS doctor
                    availableslots = self.getavailableslots(doctor_id=selected_doc.id)
                    if availableslots:
                        slotstext = "\n".join([f"• {slot['date']} at {slot['time']} with {slot['doctor']}" for slot in availableslots[:3]])
                        return self._create_json_response(
                            f"I've found {selected_doc.name} for you. Here are their upcoming openings:\n{slotstext}\n\nWhich time works best?",
                            {"intent": "booking", "step": "offer_slots", "slots": availableslots[:3]}
                        )
                else:
                    return self._create_json_response(
                        "I couldn't find a doctor by that name. Could you say the name again, or just say 'any'?",
                         {"intent": "booking", "step": "ask_doctor_retry"}
                    )
            else:
                state["awaitingdoctorpref"] = True
                return self._create_json_response(
                     "Do you have a preferred doctor?",
                    {"intent": "booking", "step": "ask_doctor"}
                )
        
        # Step 4: Book appointment
        if state.get("patientid") or state.get("userid"):
            appointment = self.createappointment(
                patientid=state.get("patientid"),
                userid=state.get("userid"),
                reason=state["appointmentreason"],
                userinput=userinput,
                doctorid=state.get("selecteddoctorid")
            )
            
            if appointment:
                return self._create_json_response(
                    f"Perfect! I've scheduled your appointment for {appointment['date']} at {appointment['time']} with {appointment['doctor']}. You'll receive a confirmation. Is there anything else I can help you with?",
                    {"intent": "booking", "step": "confirmed", "appointment": appointment}
                )
        else:
            # Fallback for unverified/no patient ID (Lead flow)
            self.save_temp_call(state.get("patientname", "Unknown"), "000-000-0000") # Need to extract phone
            return self._create_json_response(
                "I've noted your request. Since you don't have an account yet, a receptionist will call you back shortly to finalize the booking. Would you like to create an account for next time?",
                {"intent": "booking", "step": "lead_capture"}
            )
            
        return self._create_json_response(
            "I'm having trouble booking that appointment. Let me transfer you to our scheduling team.",
            {"intent": "booking", "step": "error", "transfer": True}
        )
    
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
                    return f"Thank you, {patientname}. For verification, could you provide your 5-digit OTID?"
                else:
                    return "I didn't catch your name. What is your full name?"
            else:
                state["awaitingname"] = True
                return "I can help you check your appointment. May I have your name, please?"
        
        if not state.get("verified"):
            if state.get("awaitingkey"):
                otid = self.extractotid(userinput)
                if otid:
                    user = self.verifyuserbyotid(otid)
                    if user:
                        if user.patient:
                            state["patientid"] = user.patient.id
                            state["patientname"] = user.patient.name
                        state["verified"] = True
                        
                        if state.get("patientid"):
                            appointments = self.getpatientappointments(state["patientid"])
                            if appointments:
                                appttext = "\n".join([
                                    f"• {appt['date']} at {appt['time']} with {appt['doctor']} - {appt['reason']}"
                                    for appt in appointments
                                ])
                                return f"Here are your upcoming appointments:\n{appttext}\n\nIs there anything else I can help you with?"
                            else:
                                return "You don't have any upcoming appointments scheduled. Would you like to book one?"
                        else:
                             return "I see your account but no patient records linked. Please contact the front desk."
                    else:
                        return "I couldn't verify that code. Could you provide your 5-digit OTID again?"
                else:
                    return "I need your 5-digit OTID for verification. What is it?"
            else:
                state["awaitingkey"] = True
                return "For security, I need your OTID. What is it?"
        
        return "I'm having trouble accessing your appointments. Let me transfer you to our staff."
    
    async def handleappointmentcancel(self, userinput: str, callid: str, conversationhistory: list) -> str:
        """Handle appointment cancellation"""
        state = self.conversationstate[callid]
        
        if not state.get("verified"):
             return "I need to verify your identity first. Please provide your name and OTID."

        if state.get("patientid"):
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
        
        return "That's a great question. For specific medical advice, I recommend scheduling an appointment. Would you like me to book one for you?"
    
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
        """Get intelligent response using LLM with JSON Mode"""
        if not self.usellm:
            return json.dumps({
                "spoken_response": "I'm here to help! Could you tell me more about what you need?",
                "metadata": {"intent": "fallback", "step": "0"}
            })
        
        try:
            contextparts = [
                f"You are a professional medical receptionist at {config.config.CLINICNAME}.",
                "You MUST respond in strictly valid JSON format.",
                "Structure your JSON response as follows:",
                "{"
                '  "spoken_response": "The text you want the TTS to speak to the patient (concise, 1-2 sentences).",'
                '  "analysis": "Brief internal thought about the patient\'s request.",'
                '  "current_step": "The current step in the triage process (1-8) or 0 if general chat.",'
                '  "is_emergency": false,',
                '  "missing_info": ["severity", "location"] (list of info you still need),'
                '  "intent": "appointment|medical|emergency|general",'
                '  "language": "en|fr" (Detect the user\'s language. Respond in the SAME language.)'
                "}",
                "Always maintain HIPAA compliance.",
                "Process: 1. Detect language (English or French). 2. Generate spoken_response IN THAT LANGUAGE. 3. Set 'language' field.",
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
                format='json',
                options={
                    "temperature": 0.2, # Lower temperature for structure
                    "numpredict": config.config.LLMMAXTOKENS
                }
            )
            
            json_str = response['message']['content'].strip()
            # Ensure it's valid JSON
            try:
                parsed = json.loads(json_str)
                return json.dumps(parsed)
            except json.JSONDecodeError:
                logger.error(f"LLM failed JSON format: {json_str}")
                return json.dumps({
                    "spoken_response": "I apologize, I missed that. Could you repeat?",
                    "metadata": {"error": "json_parse_error"}
                })
            
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return json.dumps({
                "spoken_response": "I apologize, I'm having trouble right now. How else can I help you?",
                "metadata": {"error": str(e)}
            })
    
    def extractpatientname(self, text: str, state: dict) -> str:
        """Extract patient name"""
        patterns = [
            r"(?:my name is|i'm|i am|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"^([A-Z][a-z]+\s+[A-Z][a-z]+)$",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).title()
        return None
    
    def extractotid(self, text: str) -> str:
        """Extract 5-digit OTID"""
        patterns = [
            r'\b(\d{5})\b',
            r'(?:code is|otid:|id is)\s*(\d{5})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def verifyuserbyotid(self, otid: str) -> User:
        """Verify user by OTID"""
        try:
            db = SessionLocal()
            user = db.query(User).filter(User.otid == otid).first()
            # Eager load patient
            if user:
                 # Accessing patient effectively loads it if using lazy loading, or we can rely on relationship
                 _ = user.patient 
            db.close()
            return user
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return None
            
    def save_temp_call(self, name: str, phone: str = "Unknown"):
        """Save temporary call record"""
        try:
            db = SessionLocal()
            temp_call = TempCall(name=name, phone=phone)
            db.add(temp_call)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Error saving temp call: {e}")

    def getpatientappointments(self, patientid: int) -> list:
        """Get patient appointments"""
        try:
            db = SessionLocal()
            today = date.today()
            appointments = db.query(Appointment).filter(
                Appointment.patientid == patientid,
                Appointment.appointmentdate >= today,
                Appointment.status == "scheduled"
            ).order_by(Appointment.appointmentdate, Appointment.appointmenttime).all()
            
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
    
    def getavailableslots(self, doctor_id: int = None, daysahead: int = 14) -> list:
        """Get available appointment slots (mock logic linked to DB)"""
        try:
            db = SessionLocal()
            today = date.today()
            slots = []
            
            # Get all doctors or specific doctor
            query = db.query(Doctor)
            if doctor_id:
                query = query.filter(Doctor.id == doctor_id)
            doctors = query.all()
            
            if not doctors:
                db.close()
                return []
                
            # Randomize doctors to check to simulate load balancing if no specific doctor
            if not doctor_id:
                 import random # Added import for random.shuffle
                 random.shuffle(doctors)
            
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
    
    
    def send_email_notification(self, type: str, appointment: Appointment):
        """Send email notification via EmailService"""
        try:
            db = SessionLocal()
            user = None
            if appointment.userid:
                user = db.query(User).filter(User.id == appointment.userid).first()
            
            if user and user.email:
                doctor = db.query(Doctor).filter(Doctor.id == appointment.doctorid).first()
                doctor_name = doctor.name if doctor else "Unknown Doctor"
                
                if type == "confirmed":
                    email_service.send_appointment_confirmation(
                        user.email, 
                        user.username, 
                        appointment.appointmentdate.strftime("%Y-%m-%d"), 
                        appointment.appointmenttime.strftime("%H:%M"), 
                        doctor_name
                    )
            db.close()
        except Exception as e:
            logger.error(f"Error triggering email service: {e}")

    def createappointment(self, patientid: int, reason: str, userinput: str, userid: int = None, doctorid: int = None) -> dict:
        """Create appointment with smart slot linking"""
        try:
            # Failsafe: If userid is missing but patientid exists, try to find the user
            if userid is None and patientid:
                try:
                    # Reverse lookup: Find user linked to this patient
                    # Assuming User.patient is a relationship, we need to query User where patient_id = patientid
                    pass # We need a session to do this query, will do it below
                except:
                    pass

            print(f"DEBUG: createappointment called with patientid={patientid}, userid={userid}", flush=True)
            db = SessionLocal()
            
            # Failsafe Logic Implementation
            if userid is None and patientid:
                linked_user = db.query(User).filter(User.patient_id == patientid).first()
                if linked_user:
                    userid = linked_user.id
                    print(f"DEBUG: Failsafe recovered userid={userid} from patientid={patientid}", flush=True)

            slots = self.getavailableslots(doctor_id=doctorid)
            
            if not slots:
                db.close()
                return None

            # Simple logic: Book the first available slot 
            # (In a real app, match 'userinput' to the specific slot time)
            selected_slot = slots[0]
            
            new_appt = Appointment(
                patientid=patientid,
                userid=userid,
                doctorid=selected_slot["doctorid"],
                appointmentdate=selected_slot["datetime"],
                appointmenttime=selected_slot["timeobj"],
                reason=reason,
                status="scheduled"
            )
            db.add(new_appt)
            db.commit()
            db.refresh(new_appt)
            
            # Send Notification
            try:
                if userid:
                    user = db.query(User).filter(User.id == userid).first()
                    if user:
                        self.send_email_notification("confirmed", new_appt)
            except:
                pass

            db.close()
            return {
                "id": new_appt.id,
                "date": selected_slot["date"],
                "time": selected_slot["time"],
                "doctor": selected_slot["doctor"]
            }
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            if 'db' in locals():
                db.close()
            return None

    def find_doctor_by_preference(self, userinput: str, reason: str) -> Doctor:
        """Find best matching doctor based on user preference or reason"""
        db = SessionLocal()
        try:
            # 1. Check if user named a specific doctor
            # Simple keyword search
            all_doctors = db.query(Doctor).all()
            for doc in all_doctors:
                if doc.name.lower() in userinput.lower() or doc.name.split()[-1].lower() in userinput.lower():
                    return doc
            
            # 2. Check for "No preference" keywords
            no_pref_keywords = ["any", "no preference", "doesn't matter", "don't care", "whoever", "recommend"]
            if any(k in userinput.lower() for k in no_pref_keywords):
                # 3. Match specialty based on reason
                reason_lower = reason.lower()
                target_specialty = "General Practice"
                
                if "heart" in reason_lower or "chest" in reason_lower:
                    target_specialty = "Cardiology"
                elif "skin" in reason_lower or "rash" in reason_lower:
                    target_specialty = "Dermatology"
                elif "child" in reason_lower or "baby" in reason_lower:
                    target_specialty = "Pediatrics"
                elif "head" in reason_lower or "migraine" in reason_lower:
                    target_specialty = "Neurology"
                
                # Find doctors with this specialty
                specialists = db.query(Doctor).filter(Doctor.specialty == target_specialty).all()
                if not specialists:
                     # Fallback to General
                     specialists = db.query(Doctor).filter(Doctor.specialty == "General Practice").all()
                
                if specialists:
                    return random.choice(specialists)
                elif all_doctors:
                     return random.choice(all_doctors)
            
            return None
        finally:
            db.close()
            

    
    def cancelappointment(self, appointmentid: int) -> bool:
        """Cancel appointment"""
        try:
            db = SessionLocal()
            appointment = db.query(Appointment).filter(Appointment.id == appointmentid).first()
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
