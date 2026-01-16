from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from db.models import Base


class MedicalEvent(Base):
    """Individual health events in patient timeline"""
    __tablename__ = "medical_events"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    event_type = Column(String, nullable=False)  # diagnosis, procedure, visit, test, medication, vaccination
    title = Column(String, nullable=False)
    description = Column(Text)
    diagnosis_code = Column(String)  # ICD-10 code
    procedure_code = Column(String)  # CPT code
    provider_name = Column(String)
    facility_name = Column(String)
    event_date = Column(Date, nullable=False, index=True)
    severity = Column(String, default="low")  # low, medium, high, critical
    status = Column(String, default="active")  # active, resolved, ongoing, follow_up_needed
    attachments = Column(JSON)  # List of document/image URLs
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id], backref="medical_events")
    anatomical_locations = relationship("AnatomicalLocation", back_populates="medical_event", cascade="all, delete-orphan")
    ai_insights = relationship("AIInsight", back_populates="medical_event", cascade="all, delete-orphan")


class AnatomicalLocation(Base):
    """Body region tagging for 3D visualization"""
    __tablename__ = "anatomical_locations"

    id = Column(Integer, primary_key=True, index=True)
    medical_event_id = Column(Integer, ForeignKey("medical_events.id"), nullable=False)
    body_region = Column(String, nullable=False)  # head, chest, abdomen, back, left_arm, right_arm, left_leg, right_leg
    body_system = Column(String)  # cardiovascular, respiratory, digestive, nervous, musculoskeletal, etc.
    specific_location = Column(String)  # e.g., "upper right quadrant", "left ventricle"
    laterality = Column(String)  # left, right, bilateral, midline
    coordinates_3d = Column(JSON)  # Optional: 3D coordinates for precise mapping
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    medical_event = relationship("MedicalEvent", back_populates="anatomical_locations")


class AIInsight(Base):
    """AI-generated summaries and recommendations"""
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    medical_event_id = Column(Integer, ForeignKey("medical_events.id"), nullable=False)
    insight_type = Column(String, nullable=False)  # key_takeaway, follow_up_status, connection, recommendation
    content = Column(Text, nullable=False)
    confidence_score = Column(Float)  # 0.0 to 1.0
    generated_at = Column(DateTime, default=datetime.now)
    generated_by = Column(String, default="llama3.1:8b")  # Model version
    reviewed_by_human = Column(Boolean, default=False)
    human_feedback = Column(Text)

    # Relationships
    medical_event = relationship("MedicalEvent", back_populates="ai_insights")


class SharedVault(Base):
    """Temporary secure links for sharing medical history"""
    __tablename__ = "shared_vaults"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    vault_token = Column(String, unique=True, index=True, nullable=False)  # Unique access token
    recipient_name = Column(String)
    recipient_email = Column(String)
    shared_events = Column(JSON)  # List of medical_event_ids to share
    two_fa_code = Column(String)  # 6-digit code
    two_fa_method = Column(String, default="email")  # email, sms
    access_count = Column(Integer, default=0)
    max_access_count = Column(Integer, default=5)  # Limit access attempts
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    last_accessed_at = Column(DateTime)
    access_log = Column(JSON)  # Track access attempts with timestamps and IPs

    # Relationships
    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id], backref="shared_vaults")
