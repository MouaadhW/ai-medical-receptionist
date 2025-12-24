from db.database import SessionLocal, initdatabase
from db.models import Patient, Doctor, Appointment, MedicalKnowledge
from datetime import datetime, date, time, timedelta
from loguru import logger
import random

def seeddatabase():
    """Seed database with sample data"""
    
    logger.info("Initializing database...")
    initdatabase()
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Patient).count() > 0:
            logger.info("Database already seeded")
            return
        
        logger.info("Seeding database with sample data...")
        
        # Sample Doctors
        doctors = [
            Doctor(
                name="Dr. Sarah Johnson",
                specialty="General Practice",
                phone="+1-555-0101",
                email="s.johnson@clinic.com",
                availabledays='["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]'
            ),
            Doctor(
                name="Dr. Michael Chen",
                specialty="Cardiology",
                phone="+1-555-0102",
                email="m.chen@clinic.com",
                availabledays='["Monday", "Wednesday", "Friday"]'
            ),
            Doctor(
                name="Dr. Emily Rodriguez",
                specialty="Pediatrics",
                phone="+1-555-0103",
                email="e.rodriguez@clinic.com",
                availabledays='["Tuesday", "Thursday", "Friday"]'
            ),
            Doctor(
                name="Dr. James Wilson",
                specialty="Orthopedics",
                phone="+1-555-0104",
                email="j.wilson@clinic.com",
                availabledays='["Monday", "Tuesday", "Wednesday", "Thursday"]'
            )
        ]
        
        for doctor in doctors:
            db.add(doctor)
        db.commit()
        logger.info(f"Added {len(doctors)} doctors")
        
        # Sample Patients
        patients = [
            Patient(
                name="John Smith",
                phone="+1-555-1001",
                email="john.smith@email.com",
                dateofbirth=date(1985, 3, 15),
                address="123 Main St, City, State 12345",
                emergencycontact="Jane Smith +1-555-1002",
                medicalhistory="Hypertension, Type 2 Diabetes",
                allergies="Penicillin",
                medications="Metformin 500mg, Lisinopril 10mg",
                insuranceinfo="Blue Cross PPO - Policy #12345",
                specialkey="SMITH1985"
            ),
            Patient(
                name="Mary Johnson",
                phone="+1-555-1003",
                email="mary.j@email.com",
                dateofbirth=date(1990, 7, 22),
                address="456 Oak Ave, City, State 12345",
                emergencycontact="Bob Johnson +1-555-1004",
                medicalhistory="Asthma",
                allergies="None",
                medications="Albuterol inhaler",
                insuranceinfo="Aetna HMO - Policy #67890",
                specialkey="JOHNSON1990"
            ),
            Patient(
                name="Robert Davis",
                phone="+1-555-1005",
                email="r.davis@email.com",
                dateofbirth=date(1978, 11, 8),
                address="789 Pine Rd, City, State 12345",
                emergencycontact="Linda Davis +1-555-1006",
                medicalhistory="High cholesterol",
                allergies="Sulfa drugs",
                medications="Atorvastatin 20mg",
                insuranceinfo="United Healthcare - Policy #11223",
                specialkey="DAVIS1978"
            ),
            Patient(
                name="Jennifer Martinez",
                phone="+1-555-1007",
                email="j.martinez@email.com",
                dateofbirth=date(1995, 5, 30),
                address="321 Elm St, City, State 12345",
                emergencycontact="Carlos Martinez +1-555-1008",
                medicalhistory="None",
                allergies="Latex",
                medications="None",
                insuranceinfo="Cigna PPO - Policy #44556",
                specialkey="MARTINEZ1995"
            ),
            Patient(
                name="William Brown",
                phone="+1-555-1009",
                email="w.brown@email.com",
                dateofbirth=date(1965, 9, 12),
                address="654 Maple Dr, City, State 12345",
                emergencycontact="Susan Brown +1-555-1010",
                medicalhistory="Arthritis, GERD",
                allergies="Aspirin",
                medications="Omeprazole 20mg, Ibuprofen 400mg",
                insuranceinfo="Medicare - Policy #77889",
                specialkey="BROWN1965"
            )
        ]
        
        for patient in patients:
            db.add(patient)
        db.commit()
        logger.info(f"Added {len(patients)} patients")
        
        # Sample Appointments
        today = date.today()
        appointments = []
        
        # Past appointments
        for i in range(3):
            pastdate = today - timedelta(days=random.randint(7, 30))
            appointments.append(
                Appointment(
                    patientid=random.randint(1, 5),
                    doctorid=random.randint(1, 4),
                    appointmentdate=pastdate,
                    appointmenttime=time(random.randint(9, 16), random.choice([0, 30])),
                    reason="Follow-up visit",
                    status="completed"
                )
            )
        
        # Future appointments
        for i in range(5):
            futuredate = today + timedelta(days=random.randint(1, 14))
            appointments.append(
                Appointment(
                    patientid=random.randint(1, 5),
                    doctorid=random.randint(1, 4),
                    appointmentdate=futuredate,
                    appointmenttime=time(random.randint(9, 16), random.choice([0, 30])),
                    reason=random.choice([
                        "Annual checkup",
                        "Follow-up visit",
                        "New patient consultation",
                        "Lab results review"
                    ]),
                    status="scheduled"
                )
            )
        
        for appointment in appointments:
            db.add(appointment)
        db.commit()
        logger.info(f"Added {len(appointments)} appointments")
        
        # Sample Medical Knowledge (from MIMIC-IV concepts)
        medicalknowledge = [
            MedicalKnowledge(
                category="symptom",
                term="Chest Pain",
                description="Discomfort or pain in the chest area, can indicate cardiac issues",
                severity="emergency",
                commonsymptoms="Pressure, tightness, squeezing sensation in chest"
            ),
            MedicalKnowledge(
                category="symptom",
                term="Fever",
                description="Elevated body temperature above 100.4°F (38°C)",
                severity="medium",
                commonsymptoms="High temperature, chills, sweating, body aches"
            ),
            MedicalKnowledge(
                category="symptom",
                term="Headache",
                description="Pain in the head or upper neck",
                severity="low",
                commonsymptoms="Throbbing, constant ache, pressure"
            ),
            MedicalKnowledge(
                category="condition",
                term="Hypertension",
                description="High blood pressure, often called the silent killer",
                icdcode="I10",
                severity="medium",
                commonsymptoms="Often no symptoms, sometimes headaches or dizziness"
            ),
            MedicalKnowledge(
                category="condition",
                term="Type 2 Diabetes",
                description="Chronic condition affecting blood sugar regulation",
                icdcode="E11",
                severity="medium",
                commonsymptoms="Increased thirst, frequent urination, fatigue"
            ),
            MedicalKnowledge(
                category="procedure",
                term="Blood Pressure Check",
                description="Measurement of arterial blood pressure",
                severity="low",
                commonsymptoms="N/A - Diagnostic procedure"
            )
        ]
        
        for knowledge in medicalknowledge:
            db.add(knowledge)
        db.commit()
        logger.info(f"Added {len(medicalknowledge)} medical knowledge entries")
        
        logger.info("Database seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if name == "main":
    seed_database()