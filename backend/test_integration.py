"""
End-to-End Integration Test for AI Medical Receptionist System
Tests all major components: API, Voice Server, Agent, and MIMIC Knowledge Base
"""

import sys
import os
import asyncio
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from loguru import logger
from db.database import SessionLocal
from db.models import Patient, Doctor, Appointment, Call, MedicalKnowledge
from agent.medical_agent import MedicalReceptionistAgent
from agent.intent_classifier import MedicalIntentClassifier
from agent.emergency_detector import EmergencyDetector
from agent.knowledge_base import MedicalKnowledgeBase
from mimic.medical_qa import MedicalQAEngine
from mimic.mimic_loader import MIMICLoader
import config

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>")


class IntegrationTestSuite:
    """Test suite for the medical receptionist system"""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []

    def test_database_connection(self):
        """Test database connectivity"""
        print("\n" + "="*70)
        print("TEST 1: Database Connection")
        print("="*70)
        try:
            db = SessionLocal()
            patient_count = db.query(Patient).count()
            doctor_count = db.query(Doctor).count()
            appointment_count = db.query(Appointment).count()
            knowledge_count = db.query(MedicalKnowledge).count()
            db.close()

            print(f"✅ Database connected")
            print(f"   📊 Patients: {patient_count}")
            print(f"   👨‍⚕️ Doctors: {doctor_count}")
            print(f"   📅 Appointments: {appointment_count}")
            print(f"   📚 Medical Knowledge: {knowledge_count}")

            self.tests_passed += 1
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.tests_failed += 1
            self.errors.append(f"DB: {str(e)}")
            return False

    def test_intent_classification(self):
        """Test intent classification"""
        print("\n" + "="*70)
        print("TEST 2: Intent Classification")
        print("="*70)
        try:
            classifier = MedicalIntentClassifier()
            test_cases = [
                ("I need to schedule an appointment", "appointmentbooking"),
                ("When is my next appointment?", "appointmentinquiry"),
                ("I have severe chest pain", "emergency"),
                ("What is hypertension?", "medicalquestion"),
                ("I need a prescription refill", "prescriptionrefill"),
                ("What are your hours?", "generalinquiry"),
            ]

            print(f"Testing {len(test_cases)} intent classifications:")
            all_pass = True
            for text, expected in test_cases:
                detected = classifier.classify(text)
                status = "✅" if detected == expected else "⚠️"
                print(f"   {status} '{text}' → {detected} (expected: {expected})")
                if detected != expected:
                    all_pass = False

            if all_pass:
                self.tests_passed += 1
            else:
                self.tests_failed += 1
                self.errors.append("Intent classification: Not all intents matched")

            return all_pass
        except Exception as e:
            print(f"❌ Intent classification failed: {e}")
            self.tests_failed += 1
            self.errors.append(f"Intent: {str(e)}")
            return False

    def test_emergency_detection(self):
        """Test emergency detection"""
        print("\n" + "="*70)
        print("TEST 3: Emergency Detection")
        print("="*70)
        try:
            detector = EmergencyDetector()
            test_cases = [
                ("I'm having severe chest pain", True, "critical"),
                ("I can't breathe", True, "critical"),
                ("I have a fever of 104", True, "urgent"),
                ("I have a headache", False, "moderate"),
                ("I'm fine", False, "none"),
            ]

            print(f"Testing {len(test_cases)} emergency scenarios:")
            all_pass = True
            for text, expected_emergency, expected_severity in test_cases:
                is_emergency, severity, advice = detector.detectemergency(text)
                status = "✅" if is_emergency == expected_emergency else "❌"
                print(f"   {status} '{text}'")
                print(f"      → Emergency: {is_emergency}, Severity: {severity}")
                if is_emergency != expected_emergency:
                    all_pass = False

            if all_pass:
                self.tests_passed += 1
            else:
                self.tests_failed += 1
                self.errors.append("Emergency detection: Not all cases detected correctly")

            return all_pass
        except Exception as e:
            print(f"❌ Emergency detection failed: {e}")
            self.tests_failed += 1
            self.errors.append(f"Emergency: {str(e)}")
            return False

    def test_knowledge_base(self):
        """Test medical knowledge base"""
        print("\n" + "="*70)
        print("TEST 4: Medical Knowledge Base")
        print("="*70)
        try:
            kb = MedicalKnowledgeBase()
            db = SessionLocal()
            knowledge_count = db.query(MedicalKnowledge).count()
            db.close()

            print(f"✅ Knowledge base initialized")
            print(f"   📚 Total medical knowledge entries: {knowledge_count}")

            # Test search
            results = db.query(MedicalKnowledge).filter(
                MedicalKnowledge.term.ilike("%Hypertension%")
            ).all()
            print(f"   🔍 Search for 'Hypertension': {len(results)} results")

            if knowledge_count > 0:
                self.tests_passed += 1
                return True
            else:
                self.tests_failed += 1
                self.errors.append("Knowledge base: No medical knowledge entries found")
                return False

        except Exception as e:
            print(f"❌ Knowledge base test failed: {e}")
            self.tests_failed += 1
            self.errors.append(f"Knowledge: {str(e)}")
            return False

    async def test_medical_agent(self):
        """Test medical agent"""
        print("\n" + "="*70)
        print("TEST 5: Medical Receptionist Agent")
        print("="*70)
        try:
            agent = MedicalReceptionistAgent()
            conversation = []

            # Test greeting
            greeting = agent.getgreeting()
            print(f"✅ Agent greeting: {greeting[:60]}...")
            conversation.append({"role": "assistant", "content": greeting})

            # Test appointment booking flow
            user_input = "I need to schedule an appointment"
            response = await agent.processinput(user_input, conversation, callid="test_001")
            print(f"✅ Booking request response: {response[:60]}...")
            conversation.append({"role": "user", "content": user_input})
            conversation.append({"role": "assistant", "content": response})

            # Test emergency handling
            emergency_input = "I'm having severe chest pain"
            response = await agent.processinput(emergency_input, conversation, callid="test_002")
            print(f"✅ Emergency response: {response[:80]}...")
            assert "emergency" in response.lower() or "911" in response.lower()

            self.tests_passed += 1
            return True

        except Exception as e:
            print(f"❌ Agent test failed: {e}")
            self.tests_failed += 1
            self.errors.append(f"Agent: {str(e)}")
            return False

    def test_patient_verification(self):
        """Test patient verification"""
        print("\n" + "="*70)
        print("TEST 6: Patient Verification")
        print("="*70)
        try:
            db = SessionLocal()
            agent = MedicalReceptionistAgent()

            # Get test patient
            patient = db.query(Patient).first()
            if not patient:
                print("⚠️  No test patients found")
                self.tests_failed += 1
                db.close()
                return False

            # Test verification
            verified = agent.verifypatientbykey(patient.name, patient.specialkey)
            if verified:
                print(f"✅ Patient verification successful")
                print(f"   👤 Patient: {verified.name}")
                print(f"   🔑 Special Key: {verified.specialkey}")
                self.tests_passed += 1
                db.close()
                return True
            else:
                print(f"❌ Patient verification failed")
                self.tests_failed += 1
                self.errors.append("Verification: Could not verify test patient")
                db.close()
                return False

        except Exception as e:
            print(f"❌ Patient verification test failed: {e}")
            self.tests_failed += 1
            self.errors.append(f"Verification: {str(e)}")
            return False

    def test_mimic_integration(self):
        """Test MIMIC loader integration"""
        print("\n" + "="*70)
        print("TEST 7: MIMIC Integration")
        print("="*70)
        try:
            loader = MIMICLoader()
            db = SessionLocal()

            # Check existing medical knowledge
            diagnoses = db.query(MedicalKnowledge).filter(
                MedicalKnowledge.category == "diagnosis"
            ).count()
            procedures = db.query(MedicalKnowledge).filter(
                MedicalKnowledge.category == "procedure"
            ).count()
            medications = db.query(MedicalKnowledge).filter(
                MedicalKnowledge.category == "medication"
            ).count()

            print(f"✅ MIMIC data integration successful")
            print(f"   🔬 Diagnoses: {diagnoses}")
            print(f"   🏥 Procedures: {procedures}")
            print(f"   💊 Medications: {medications}")

            if diagnoses + procedures + medications > 0:
                self.tests_passed += 1
                db.close()
                return True
            else:
                self.tests_failed += 1
                self.errors.append("MIMIC: No medical knowledge data found")
                db.close()
                return False

        except Exception as e:
            print(f"❌ MIMIC integration test failed: {e}")
            self.tests_failed += 1
            self.errors.append(f"MIMIC: {str(e)}")
            return False

    def test_api_endpoints(self):
        """Test API endpoints availability"""
        print("\n" + "="*70)
        print("TEST 8: API Endpoints")
        print("="*70)
        try:
            from api.server import app
            from api.routes import router

            print(f"✅ API server imported successfully")
            print(f"   📡 App title: {app.title}")
            print(f"   🔗 API routes available:")

            # List routes
            route_count = 0
            for route in app.routes:
                if hasattr(route, 'path'):
                    if route.path.startswith('/api'):
                        route_count += 1
                        methods = getattr(route, 'methods', ['GET'])
                        print(f"      {route.path} {list(methods)}")

            print(f"   📊 Total API routes: {route_count}")

            if route_count > 0:
                self.tests_passed += 1
                return True
            else:
                self.tests_failed += 1
                self.errors.append("API: No routes found")
                return False

        except Exception as e:
            print(f"❌ API endpoints test failed: {e}")
            self.tests_failed += 1
            self.errors.append(f"API: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "="*80)
        print(" "*20 + "[HOSPITAL] AI MEDICAL RECEPTIONIST")
        print(" "*15 + "END-TO-END INTEGRATION TEST SUITE")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Configuration: {config.config.APPNAME} v{config.config.VERSION}")
        print("="*80)

        # Run all tests
        self.test_database_connection()
        self.test_intent_classification()
        self.test_emergency_detection()
        self.test_knowledge_base()
        self.test_patient_verification()
        self.test_mimic_integration()
        self.test_api_endpoints()
        await self.test_medical_agent()

        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        total = self.tests_passed + self.tests_failed
        percentage = (self.tests_passed / total * 100) if total > 0 else 0

        print(f"[OK] Passed: {self.tests_passed}")
        print(f"[FAIL] Failed: {self.tests_failed}")
        print(f"[INFO] Total:  {total}")
        print(f"[STATS] Success Rate: {percentage:.1f}%")

        if self.errors:
            print("\n[WARNING] Errors:")
            for error in self.errors:
                print(f"   * {error}")

        print("\n" + "="*80)

        if self.tests_failed == 0:
            print("[OK] ALL TESTS PASSED - System is ready to deploy!")
        else:
            print(f"[WARNING] {self.tests_failed} test(s) failed - Review errors above")

        print("="*80 + "\n")

        return self.tests_failed == 0


async def main():
    """Main test runner"""
    suite = IntegrationTestSuite()
    success = await suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
