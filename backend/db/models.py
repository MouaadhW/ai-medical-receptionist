from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Date, Time
from sqlalchemy.ext.declarative import declarativebase
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarativebase()

class Patient(Base):
    """Patient information"""
    tablename = "patients"
    
    id = Column(Integer, primarykey=True, index=True)
    name = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False, index=True)
    email = Column(String)
    dateofbirth = Column(Date)
    address = Column(String)
    emergencycontact = Column(String)
    medicalhistory = Column(Text)
    allergies = Column(Text)
    medications = Column(Text)
    insuranceinfo = Column(String)
    specialkey = Column(String, unique=True, index=True)  # For phone verification
    createdat = Column(DateTime, default=datetime.now)
    updatedat = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    appointments = relationship("Appointment", backpopulates="patient")
    calls = relationship("Call", backpopulates="patient")

class Doctor(Base):
    """Doctor information"""
    tablename = "doctors"
    
    id = Column(Integer, primarykey=True, index=True)
    name = Column(String, nullable=False)
    specialty = Column(String)
    phone = Column(String)
    email = Column(String)
    availabledays = Column(String)  # JSON string of available days
    createdat = Column(DateTime, default=datetime.now)
    
    # Relationships
    appointments = relationship("Appointment", backpopulates="doctor")

class Appointment(Base):
    """Appointment scheduling"""
    tablename = "appointments"
    
    id = Column(Integer, primarykey=True, index=True)
    patientid = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctorid = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointmentdate = Column(Date, nullable=False, index=True)
    appointmenttime = Column(Time, nullable=False)
    durationminutes = Column(Integer, default=30)
    reason = Column(Text)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled, no-show
    notes = Column(Text)
    createdat = Column(DateTime, default=datetime.now)
    updatedat = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    patient = relationship("Patient", backpopulates="appointments")
    doctor = relationship("Doctor", backpopulates="appointments")

class Call(Base):
    """Call records"""
    tablename = "calls"
    
    id = Column(Integer, primarykey=True, index=True)
    patientid = Column(Integer, ForeignKey("patients.id"), nullable=True)
    callernumber = Column(String)
    callername = Column(String)
    starttime = Column(DateTime, default=datetime.now)
    endtime = Column(DateTime)
    duration = Column(Integer)  # seconds
    intent = Column(String)  # appointment, inquiry, emergency, etc.
    transcript = Column(Text)
    summary = Column(Text)
    status = Column(String)  # completed, missed, emergency
    emergencydetected = Column(Boolean, default=False)
    appointmentcreated = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    createdat = Column(DateTime, default=datetime.now)
    
    # Relationships
    patient = relationship("Patient", backpopulates="calls")

class MedicalKnowledge(Base):
    """Medical knowledge base from MIMIC-IV"""
    tablename = "medicalknowledge"
    
    id = Column(Integer, primarykey=True, index=True)
    category = Column(String, index=True)  # diagnosis, procedure, medication, etc.
    term = Column(String, index=True)
    description = Column(Text)
    icdcode = Column(String)
    severity = Column(String)  # low, medium, high, emergency
    commonsymptoms = Column(Text)
    createdat = Column(DateTime, default=datetime.now)