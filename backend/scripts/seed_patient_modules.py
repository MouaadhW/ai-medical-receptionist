"""
Sample Data Generator for Billing and Medical History
Run this to populate database with demo data for testing
"""

from datetime import datetime, timedelta, date
from db.database import SessionLocal
from db.billing import Bill, BillItem, Payment
from db.medical_history import MedicalEvent, AnatomicalLocation, AIInsight
from db.models import Patient
import random


def seed_billing_data():
    """Seed sample billing data"""
    db = SessionLocal()
    
    try:
        # Get existing patients
        patients = db.query(Patient).limit(5).all()
        
        if not patients:
            print("No patients found. Seed main database first.")
            return
        
        for patient in patients:
            # Create 2-3 bills per patient
            for i in range(random.randint(2, 3)):
                # Create bill
                bill_number = f"BILL-2026-{random.randint(1000, 9999)}"
                total_amount = random.uniform(150, 500)
                insurance_covered = total_amount * 0.75 if random.random() > 0.3 else 0
                patient_due = total_amount - insurance_covered
                
                bill = Bill(
                    patient_id=patient.id,
                    bill_number=bill_number,
                    total_amount=total_amount,
                    insurance_covered=insurance_covered,
                    patient_due=patient_due,
                    status=random.choice(['paid', 'pending', 'partial']),
                    billed_date=datetime.now() - timedelta(days=random.randint(1, 60)),
                    due_date=datetime.now() + timedelta(days=random.randint(7, 30))
                )
                db.add(bill)
                db.flush()  # Get bill.id
                
                # Create bill items
                categories = [
                    ('consultation', 'Initial Consultation - Dr. Smith', 80),
                    ('lab_test', 'Complete Blood Count (CBC)', 45),
                    ('lab_test', 'Thyroid Function Test', 65),
                    ('medication', 'Prescription Medication - 30 days', 30),
                    ('imaging', 'Chest X-Ray', 120),
                    ('procedure', 'Minor Procedure', 200)
                ]
                
                num_items = random.randint(2, 4)
                selected_items = random.sample(categories, num_items)
                
                for category, description, unit_price in selected_items:
                    item = BillItem(
                        bill_id=bill.id,
                        category=category,
                        description=description,
                        quantity=1,
                        unit_price=unit_price,
                        total_price=unit_price,
                        necessity_level=random.choice(['essential', 'recommended', 'optional'])
                    )
                    db.add(item)
        
        db.commit()
        print(f"✅ Seeded billing data for {len(patients)} patients")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding billing data: {e}")
    finally:
        db.close()


def seed_medical_history_data():
    """Seed sample medical history timeline data"""
    db = SessionLocal()
    
    try:
        patients = db.query(Patient).limit(5).all()
        
        if not patients:
            print("No patients found. Seed main database first.")
            return
        
        for patient in patients:
            # Create 5-10 medical events per patient
            events_data = [
                {
                    'event_type': 'diagnosis',
                    'title': 'Hypertension Diagnosis',
                    'description': 'Blood pressure consistently above 140/90',
                    'severity': 'medium',
                    'body_region': 'chest',
                    'body_system': 'cardiovascular'
                },
                {
                    'event_type': 'visit',
                    'title': 'Annual Physical Examination',
                    'description': 'Routine checkup - all vitals normal',
                    'severity': 'low',
                    'body_region': 'chest',
                    'body_system': 'general'
                },
                {
                    'event_type': 'test',
                    'title': 'Blood Work - Complete Panel',
                    'description': 'Cholesterol slightly elevated',
                    'severity': 'low',
                    'body_region': 'left_arm',
                    'body_system': 'cardiovascular'
                },
                {
                    'event_type': 'procedure',
                    'title': 'Minor Skin Lesion Removal',
                    'description': 'Benign lesion removed from left shoulder',
                    'severity': 'low',
                    'body_region': 'left_arm',
                    'body_system': 'integumentary'
                },
                {
                    'event_type': 'vaccination',
                    'title': 'Flu Vaccine',
                    'description': 'Annual influenza vaccination',
                    'severity': 'low',
                    'body_region': 'left_arm',
                    'body_system': 'immune'
                },
                {
                    'event_type': 'diagnosis',
                    'title': 'Type 2 Diabetes Mellitus',
                    'description': 'HbA1c at 7.2%, started on Metformin',
                    'severity': 'high',
                    'body_region': 'abdomen',
                    'body_system': 'endocrine'
                },
            ]
            
            num_events = random.randint(4, 8)
            selected_events = random.sample(events_data, num_events)
            
            for idx, event_data in enumerate(selected_events):
                # Create event with date in past
                days_ago = random.randint(30, 1095)  # 1 month to 3 years ago
                event_date = date.today() - timedelta(days=days_ago)
                
                event = MedicalEvent(
                    patient_id=patient.id,
                    event_type=event_data['event_type'],
                    title=event_data['title'],
                    description=event_data['description'],
                    event_date=event_date,
                    severity=event_data['severity'],
                    status=random.choice(['active', 'resolved', 'ongoing']),
                    provider_name=random.choice(['Dr. Smith', 'Dr. Johnson', 'Dr. Williams']),
                    facility_name='MedPulse Clinic'
                )
                db.add(event)
                db.flush()  # Get event.id
                
                # Add anatomical location
                location = AnatomicalLocation(
                    medical_event_id=event.id,
                    body_region=event_data['body_region'],
                    body_system=event_data['body_system'],
                    laterality='left' if 'left' in event_data['body_region'] else 'right' if 'right' in event_data['body_region'] else 'bilateral'
                                )
                db.add(location)
                
                # Add AI insight (key takeaway)
                insight = AIInsight(
                    medical_event_id=event.id,
                    insight_type='key_takeaway',
                    content=f"This {event_data['event_type']} was important for tracking your overall health progression.",
                    confidence_score=0.85
                )
                db.add(insight)
        
        db.commit()
        print(f"✅ Seeded medical history data for {len(patients)} patients")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding medical history data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding sample data for MedPulse patient-centric modules...")
    seed_billing_data()
    seed_medical_history_data()
    print("✨ Sample data seeding complete!")
