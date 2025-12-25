"""
Urgent Care Handler
Implements 8-step medical triage process with medically-advised procedures
"""

from loguru import logger
from typing import Dict, List, Optional
from mimic.urgent_care_knowledge import URGENT_CARE_KNOWLEDGE


class UrgentCareHandler:
    """
    Handles urgent medical cases with proper triage and first-aid guidance
    Follows 8-step thinking process for medical assessment
    """
    
    def __init__(self):
        self.knowledge_base = URGENT_CARE_KNOWLEDGE
        logger.info("Urgent Care Handler initialized")
    
    def handle_medical_concern(self, symptoms: str, patient_responses: Dict = None) -> Dict:
        """
        Process medical concern through 8-step framework
        
        Args:
            symptoms: Patient's described symptoms
            patient_responses: Answers to assessment questions
            
        Returns:
            Dict containing structured medical guidance
        """
        
        # Find matching condition
        condition_data = self._match_condition(symptoms)
        
        if not condition_data:
            return self._generic_medical_response(symptoms)
        
        # Execute 8-step protocol
        return self._eight_step_protocol(condition_data, symptoms, patient_responses)
    
    def _match_condition(self, symptoms: str) -> Optional[Dict]:
        """Match symptoms to known conditions"""
        symptoms_lower = symptoms.lower()
        
        # Check for exact matches or keyword matches
        for condition_key, data in self.knowledge_base.items():
            # Check term
            if data['term'].lower() in symptoms_lower:
                return data
            
            # Check symptoms list
            for symptom in data.get('symptoms', []):
                if symptom.lower() in symptoms_lower:
                    return data
            
            # Check keywords in condition key
            keywords = condition_key.split('_')
            if any(keyword in symptoms_lower for keyword in keywords):
                return data
        
        return None
    
    def _eight_step_protocol(self, condition: Dict, symptoms: str, responses: Dict = None) -> Dict:
        """
        Execute 8-step medical thinking process:
        1. Acknowledge the concern
        2. Assess severity (ask key questions if needed)
        3. Classify triage level
        4. Provide appropriate guidance
        5. Give first-aid steps (if applicable)
        6. Explain red flags to watch for
        7. Include disclaimer
        8. Offer to schedule follow-up appointment
        """
        
        triage_level = condition['triage_level']
        
        # Build structured response
        response = {
            'condition': condition['term'],
            'triage_level': triage_level,
            'steps': []
        }
        
        # STEP 1: Acknowledge the concern
        acknowledgment = self._step1_acknowledge(condition, symptoms)
        response['steps'].append({
            'step': 1,
            'title': 'Acknowledgment',
            'content': acknowledgment
        })
        
        # STEP 2: Assess severity
        assessment = self._step2_assess(condition, responses)
        response['steps'].append({
            'step': 2,
            'title': 'Assessment',
            'content': assessment
        })
        
        # STEP 3: Classify triage level
        triage = self._step3_triage(condition)
        response['steps'].append({
            'step': 3,
            'title': 'Triage Classification',
            'content': triage
        })
        
        # STEP 4: Provide appropriate guidance
        guidance = self._step4_guidance(condition, triage_level)
        response['steps'].append({
            'step': 4,
            'title': 'Immediate Guidance',
            'content': guidance
        })
        
        # STEP 5: Give first-aid steps
        if condition.get('first_aid'):
            first_aid = self._step5_first_aid(condition)
            response['steps'].append({
                'step': 5,
                'title': 'First-Aid Instructions',
                'content': first_aid
            })
        
        # STEP 6: Explain red flags
        red_flags = self._step6_red_flags(condition)
        response['steps'].append({
            'step': 6,
            'title': 'Warning Signs',
            'content': red_flags
        })
        
        # STEP 7: Include disclaimer
        disclaimer = self._step7_disclaimer(condition)
        response['steps'].append({
            'step': 7,
            'title': 'Medical Disclaimer',
            'content': disclaimer
        })
        
        # STEP 8: Offer follow-up
        followup = self._step8_followup(triage_level)
        response['steps'].append({
            'step': 8,
            'title': 'Follow-Up Care',
            'content': followup
        })
        
        # Add formatted response text
        response['formatted_response'] = self._format_response(response)
        
        return response
    
    def _step1_acknowledge(self, condition: Dict, symptoms: str) -> str:
        """Step 1: Acknowledge the concern empathetically"""
        return (
            f"I understand you're experiencing {symptoms}. "
            f"I'm here to help assess this situation. "
            f"Let me gather some information to provide you with the best guidance."
        )
    
    def _step2_assess(self, condition: Dict, responses: Dict = None) -> Dict:
        """Step 2: Assess severity through key questions"""
        questions = condition.get('assessment_questions', [])
        
        assessment = {
            'questions': questions,
            'description': condition['description']
        }
        
        if responses:
            assessment['responses_received'] = True
        else:
            assessment['responses_received'] = False
            assessment['message'] = "I need to ask you a few questions to assess the severity:"
        
        return assessment
    
    def _step3_triage(self, condition: Dict) -> Dict:
        """Step 3: Classify triage level"""
        triage_level = condition['triage_level']
        
        triage_info = {
            'level': triage_level,
            'category': condition['category']
        }
        
        if triage_level == 'EMERGENCY':
            triage_info['urgency'] = 'IMMEDIATE - Life-threatening situation'
            triage_info['action'] = 'Call 911 immediately'
        elif triage_level == 'URGENT':
            triage_info['urgency'] = 'HIGH - Requires medical attention soon'
            triage_info['action'] = 'Seek medical care within hours'
        else:
            triage_info['urgency'] = 'ROUTINE - Can be managed with first-aid'
            triage_info['action'] = 'Follow first-aid steps and monitor'
        
        return triage_info
    
    def _step4_guidance(self, condition: Dict, triage_level: str) -> Dict:
        """Step 4: Provide appropriate guidance based on triage level"""
        guidance = {
            'immediate_action': condition.get('immediate_action', ''),
            'triage_specific': ''
        }
        
        if triage_level == 'EMERGENCY':
            guidance['triage_specific'] = (
                "🚨 **THIS IS AN EMERGENCY** 🚨\n\n"
                f"{condition.get('immediate_action', 'Call 911 immediately')}\n\n"
                "Do NOT wait. Do NOT drive yourself. Call emergency services now."
            )
        elif triage_level == 'URGENT':
            when_to_seek = condition.get('when_to_seek_care', [])
            timeframe = "within a few hours"
            if when_to_seek:
                guidance['triage_specific'] = (
                    f"⚠️ **SEEK MEDICAL CARE {timeframe.upper()}** ⚠️\n\n"
                    f"While this may not be immediately life-threatening, it requires "
                    f"professional medical evaluation {timeframe}.\n\n"
                    f"Go to urgent care or emergency room if:\n" + 
                    "\n".join(f"• {item}" for item in when_to_seek)
                )
        else:
            guidance['triage_specific'] = (
                "This can typically be managed at home with proper first-aid. "
                "Follow the instructions below carefully."
            )
        
        return guidance
    
    def _step5_first_aid(self, condition: Dict) -> Dict:
        """Step 5: Provide first-aid instructions"""
        first_aid_steps = condition.get('first_aid', [])
        do_not_steps = condition.get('do_not', [])
        
        return {
            'do_steps': first_aid_steps,
            'do_not_steps': do_not_steps,
            'formatted': self._format_first_aid_steps(first_aid_steps, do_not_steps)
        }
    
    def _format_first_aid_steps(self, do_steps: List[str], do_not_steps: List[str]) -> str:
        """Format first-aid steps clearly"""
        formatted = "**WHAT TO DO:**\n\n"
        for i, step in enumerate(do_steps, 1):
            formatted += f"{i}. {step}\n"
        
        if do_not_steps:
            formatted += "\n**DO NOT:**\n\n"
            for step in do_not_steps:
                formatted += f"❌ {step}\n"
        
        return formatted
    
    def _step6_red_flags(self, condition: Dict) -> Dict:
        """Step 6: Explain red flags/warning signs"""
        red_flags = condition.get('red_flags', [])
        
        return {
            'warning_signs': red_flags,
            'formatted': (
                "⚠️ **SEEK IMMEDIATE MEDICAL ATTENTION IF:**\n\n" +
                "\n".join(f"🚩 {flag}" for flag in red_flags)
            )
        }
    
    def _step7_disclaimer(self, condition: Dict) -> Dict:
        """Step 7: Include appropriate medical disclaimer"""
        source = condition.get('source', 'Medical Guidelines')
        source_url = condition.get('source_url', '')
        
        disclaimer_text = (
            f"**MEDICAL DISCLAIMER:**\n\n"
            f"This information is based on general medical guidelines from {source} "
            f"and is provided for educational purposes only. It does NOT replace "
            f"professional medical diagnosis, advice, or treatment.\n\n"
            f"Every medical situation is unique. When in doubt, always seek "
            f"professional medical care. If this is an emergency, call 911 immediately.\n\n"
        )
        
        if source_url:
            disclaimer_text += f"Source: {source}\n{source_url}\n"
        
        return {
            'text': disclaimer_text,
            'source': source,
            'source_url': source_url
        }
    
    def _step8_followup(self, triage_level: str) -> Dict:
        """Step 8: Offer to schedule follow-up appointment"""
        if triage_level == 'EMERGENCY':
            message = (
                "After you receive emergency care, please follow up with our clinic "
                "for continued care. Once you're stable, I can help schedule a "
                "follow-up appointment with one of our doctors."
            )
        elif triage_level == 'URGENT':
            message = (
                "After you receive urgent medical care, I recommend scheduling a "
                "follow-up appointment with one of our doctors. Would you like me "
                "to schedule that for you now, or after your urgent care visit?"
            )
        else:
            message = (
                "If your condition doesn't improve with first-aid within 24-48 hours, "
                "or if it worsens, please make an appointment with one of our doctors. "
                "Would you like me to schedule an appointment for you?"
            )
        
        return {
            'offer': message,
            'can_schedule_now': triage_level == 'ROUTINE'
        }
    
    def _format_response(self, response_data: Dict) -> str:
        """Format complete response for patient"""
        formatted = f"\n{'='*60}\n"
        formatted += f"MEDICAL ASSESSMENT: {response_data['condition']}\n"
        formatted += f"TRIAGE LEVEL: {response_data['triage_level']}\n"
        formatted += f"{'='*60}\n\n"
        
        for step in response_data['steps']:
            formatted += f"**{step['title']}**\n\n"
            
            content = step['content']
            if isinstance(content, dict):
                if 'formatted' in content:
                    formatted += content['formatted'] + "\n\n"
                elif 'text' in content:
                    formatted += content['text'] + "\n\n"
                else:
                    formatted += str(content) + "\n\n"
            else:
                formatted += str(content) + "\n\n"
            
            formatted += "-" * 60 + "\n\n"
        
        return formatted
    
    def _generic_medical_response(self, symptoms: str) -> Dict:
        """Handle cases where no specific condition matches"""
        return {
            'condition': 'General Medical Concern',
            'triage_level': 'UNKNOWN',
            'response': (
                f"I understand you're experiencing {symptoms}. While I don't have "
                f"specific guidance for this particular concern in my knowledge base, "
                f"I recommend the following:\n\n"
                f"1. If symptoms are severe or worsening, seek medical care immediately\n"
                f"2. If you're experiencing any emergency symptoms (severe pain, "
                f"difficulty breathing, chest pain, severe bleeding), call 911\n"
                f"3. For non-emergency concerns, schedule an appointment with one of our doctors\n\n"
                f"Would you like me to help you schedule an appointment?"
            )
        }
    
    def get_condition_list(self, category: str = None) -> List[str]:
        """Get list of conditions in knowledge base"""
        if category:
            return [
                data['term'] for data in self.knowledge_base.values()
                if data['category'] == category
            ]
        return [data['term'] for data in self.knowledge_base.values()]
