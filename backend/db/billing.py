from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from db.models import Base  # Use shared Base

class Bill(Base):
    """Patient billing records"""
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    bill_number = Column(String, unique=True, index=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    insurance_covered = Column(Float, default=0.0)
    patient_due = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, paid, overdue, partial
    billed_date = Column(DateTime, default=datetime.now)
    due_date = Column(DateTime, nullable=True)
    paid_date = Column(DateTime, nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id], backref="bills")
    items = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="bill", cascade="all, delete-orphan")
    insurance_claim = relationship("InsuranceClaim", back_populates="bill", uselist=False)


class BillItem(Base):
    """Individual line items in a bill"""
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    category = Column(String, nullable=False)  # consultation, lab_test, medication, procedure, imaging
    description = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    necessity_level = Column(String, default="essential")  # essential, recommended, optional
    ai_explanation = Column(Text)  # AI-generated explanation for this charge
    related_medical_event_id = Column(Integer, nullable=True)  # Link to medical history
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    bill = relationship("Bill", back_populates="items")


class Payment(Base):
    """Payment transactions"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)  # d17, flouci, cnam, cash, card
    payment_gateway = Column(String)  # d17, flouci, etc.
    transaction_id = Column(String, unique=True, index=True)
    status = Column(String, default="pending")  # pending, completed, failed, refunded
    payment_date = Column(DateTime, default=datetime.now)
    gateway_response = Column(JSON)  # Store gateway API response
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    bill = relationship("Bill", back_populates="payments")


class InsuranceClaim(Base):
    """CNAM insurance claim tracking"""
    __tablename__ = "insurance_claims"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    claim_number = Column(String, unique=True, index=True)
    insurance_provider = Column(String, default="CNAM")
    claim_amount = Column(Float, nullable=False)
    approved_amount = Column(Float, default=0.0)
    status = Column(String, default="submitted")  # submitted, under_review, approved, rejected, paid
    submitted_date = Column(DateTime, default=datetime.now)
    decision_date = Column(DateTime)
    payment_date = Column(DateTime)
    rejection_reason = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    bill = relationship("Bill", back_populates="insurance_claim")
    patient = relationship("Patient", foreign_keys=[patient_id], backref="insurance_claims")


class CostPrediction(Base):
    """AI-generated cost predictions for future visits"""
    __tablename__ = "cost_predictions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    predicted_visit_type = Column(String)  # follow_up, routine_checkup, specialist, etc.
    predicted_min_cost = Column(Float, nullable=False)
    predicted_max_cost = Column(Float, nullable=False)
    predicted_avg_cost = Column(Float, nullable=False)
    confidence_level = Column(Float)  # 0.0 to 1.0
    breakdown = Column(JSON)  # Detailed cost breakdown by category
    based_on_history = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    valid_until = Column(DateTime)  # Prediction expiration

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id], backref="cost_predictions")
