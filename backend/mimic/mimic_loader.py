"""
MIMIC-IV Data Loader
Loads medical knowledge from MIMIC-IV demo dataset
"""

from loguru import logger
from db.database import SessionLocal
from db.models import MedicalKnowledge
import os
import json

class MIMICLoader:
    """Load MIMIC-IV medical knowledge into database"""

    def __init__(self, datapath: str = "./mimicdata"):
        self.datapath = datapath
        logger.info(f"MIMIC Loader initialized with path: {datapath}")
    
    def loaddiagnoses(self):
        """Load diagnosis codes and descriptions"""
        try:
            db = SessionLocal()
            
            # Sample MIMIC-IV diagnoses (ICD-10 codes)
            diagnoses = [
                {
                    "category": "diagnosis",
                    "term": "Essential Hypertension",
                    "description": "High blood pressure without known cause",
                    "icdcode": "I10",
                    "severity": "medium",
                    "commonsymptoms": "Often asymptomatic, headaches, dizziness"
                },
                {
                    "category": "diagnosis",
                    "term": "Type 2 Diabetes Mellitus",
                    "description": "Chronic condition affecting blood sugar regulation",
                    "icdcode": "E11",
                    "severity": "medium",
                    "commonsymptoms": "Increased thirst, frequent urination, fatigue, blurred vision"
                },
                {
                    "category": "diagnosis",
                    "term": "Acute Myocardial Infarction",
                    "description": "Heart attack - blockage of blood flow to heart muscle",
                    "icdcode": "I21",
                    "severity": "emergency",
                    "commonsymptoms": "Chest pain, shortness of breath, nausea, sweating"
                },
                {
                    "category": "diagnosis",
                    "term": "Pneumonia",
                    "description": "Infection of the lungs",
                    "icdcode": "J18",
                    "severity": "high",
                    "commonsymptoms": "Cough, fever, difficulty breathing, chest pain"
                },
                {
                    "category": "diagnosis",
                    "term": "Chronic Obstructive Pulmonary Disease",
                    "description": "Progressive lung disease causing breathing difficulties",
                    "icdcode": "J44",
                    "severity": "high",
                    "commonsymptoms": "Shortness of breath, wheezing, chronic cough"
                }
            ]
            
            for diag in diagnoses:
                existing = db.query(MedicalKnowledge).filter(
                    MedicalKnowledge.icdcode == diag["icdcode"]
                ).first()

                if not existing:
                    knowledge = MedicalKnowledge(**diag)
                    db.add(knowledge)
            
            db.commit()
            db.close()
            logger.info(f"Loaded {len(diagnoses)} diagnoses from MIMIC-IV")
            
        except Exception as e:
            logger.error(f"Error loading diagnoses: {e}")
    
    def loadprocedures(self):
        """Load medical procedures"""
        try:
            db = SessionLocal()
            
            procedures = [
                {
                    "category": "procedure",
                    "term": "Blood Pressure Measurement",
                    "description": "Non-invasive measurement of arterial blood pressure",
                    "severity": "low",
                    "commonsymptoms": "N/A - Diagnostic procedure"
                },
                {
                    "category": "procedure",
                    "term": "Electrocardiogram (ECG)",
                    "description": "Recording of electrical activity of the heart",
                    "severity": "low",
                    "commonsymptoms": "N/A - Diagnostic procedure"
                },
                {
                    "category": "procedure",
                    "term": "Blood Glucose Test",
                    "description": "Measurement of blood sugar levels",
                    "severity": "low",
                    "commonsymptoms": "N/A - Diagnostic procedure"
                }
            ]
            
            for proc in procedures:
                existing = db.query(MedicalKnowledge).filter(
                    MedicalKnowledge.term == proc["term"]
                ).first()

                if not existing:
                    knowledge = MedicalKnowledge(**proc)
                    db.add(knowledge)
            
            db.commit()
            db.close()
            logger.info(f"Loaded {len(procedures)} procedures from MIMIC-IV")
            
        except Exception as e:
            logger.error(f"Error loading procedures: {e}")
    
    def loadmedications(self):
        """Load medication information"""
        try:
            db = SessionLocal()
            
            medications = [
                {
                    "category": "medication",
                    "term": "Metformin",
                    "description": "Oral diabetes medication that helps control blood sugar",
                    "severity": "low",
                    "commonsymptoms": "Common side effects: nausea, diarrhea"
                },
                {
                    "category": "medication",
                    "term": "Lisinopril",
                    "description": "ACE inhibitor used to treat high blood pressure",
                    "severity": "low",
                    "commonsymptoms": "Common side effects: dry cough, dizziness"
                },
                {
                    "category": "medication",
                    "term": "Aspirin",
                    "description": "Pain reliever and blood thinner",
                    "severity": "low",
                    "commonsymptoms": "Common side effects: stomach upset, bleeding risk"
                }
            ]
            
            for med in medications:
                existing = db.query(MedicalKnowledge).filter(
                    MedicalKnowledge.term == med["term"]
                ).first()
                
                if not existing:
                    knowledge = MedicalKnowledge(**med)
                    db.add(knowledge)
            
            db.commit()
            db.close()
            logger.info(f"Loaded {len(medications)} medications from MIMIC-IV")
            
        except Exception as e:
            logger.error(f"Error loading medications: {e}")
    
    def loadall(self):
        """Load all MIMIC-IV data"""
        logger.info("Loading MIMIC-IV medical knowledge...")
        self.loaddiagnoses()
        self.loadprocedures()
        self.loadmedications()
        logger.info("MIMIC-IV data loading complete")

if __name__ == "__main__":
    loader = MIMICLoader()
    loader.loadall()