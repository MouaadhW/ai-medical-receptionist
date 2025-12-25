from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime


Base = declarative_base()


class Patient(Base):
    """Patient information"""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
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
    appointments = relationship("Appointment", back_populates="patient")
    calls = relationship("Call", back_populates="patient")


class Doctor(Base):
    """Doctor information"""
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialty = Column(String)
    phone = Column(String)
    email = Column(String)
    availabledays = Column(String)  # JSON string of available days
    createdat = Column(DateTime, default=datetime.now)

    # Relationships
    appointments = relationship("Appointment", back_populates="doctor")


class Appointment(Base):
    """Appointment scheduling"""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
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
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")


class Call(Base):
    """Call records"""
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
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
    patient = relationship("Patient", back_populates="calls")


class MedicalKnowledge(Base):
    """Medical knowledge base from MIMIC-IV"""
    __tablename__ = "medicalknowledge"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)  # diagnosis, procedure, medication, etc.
    term = Column(String, index=True)
    description = Column(Text)
    icdcode = Column(String)
    severity = Column(String)  # low, medium, high, emergency
    commonsymptoms = Column(Text)
    createdat = Column(DateTime, default=datetime.now)