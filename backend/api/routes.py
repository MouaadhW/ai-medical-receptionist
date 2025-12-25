from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.database import getdb
from db.models import Patient, Doctor, Appointment, Call, MedicalKnowledge
from datetime import date, datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()


# Pydantic models
class PatientResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str]
    dateofbirth: Optional[date]

    class Config:
        orm_mode = True


class AppointmentResponse(BaseModel):
    id: int
    patientid: int
    doctorid: int
    appointmentdate: date
    appointmenttime: str
    reason: Optional[str]
    status: str

    class Config:
        orm_mode = True


class CallResponse(BaseModel):
    id: int
    callername: Optional[str]
    starttime: datetime
    duration: Optional[int]
    intent: Optional[str]
    status: str
    emergencydetected: bool

    class Config:
        orm_mode = True


# Patients
@router.get("/patients", response_model=List[PatientResponse])
async def getpatients(skip: int = 0, limit: int = 100, db: Session = Depends(getdb)):
    """Get all patients"""
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients


@router.get("/patients/{patientid}", response_model=PatientResponse)
async def getpatient(patientid: int, db: Session = Depends(getdb)):
    """Get patient by ID"""
    patient = db.query(Patient).filter(Patient.id == patientid).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/patients/search/{name}")
async def searchpatients(name: str, db: Session = Depends(getdb)):
    """Search patients by name"""
    patients = db.query(Patient).filter(Patient.name.ilike(f"%{name}%")).limit(10).all()
    return [{"id": p.id, "name": p.name, "phone": p.phone} for p in patients]


# Doctors
@router.get("/doctors")
async def getdoctors(db: Session = Depends(getdb)):
    """Get all doctors"""
    doctors = db.query(Doctor).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "specialty": d.specialty,
            "phone": d.phone,
            "email": d.email,
        }
        for d in doctors
    ]


# Appointments
@router.get("/appointments", response_model=List[AppointmentResponse])
async def getappointments(
    patientid: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(getdb),
):
    """Get appointments"""
    query = db.query(Appointment)

    if patientid:
        query = query.filter(Appointment.patientid == patientid)
    if status:
        query = query.filter(Appointment.status == status)

    appointments = query.order_by(Appointment.appointmentdate.desc()).all()

    result = []
    for appt in appointments:
        apptdict = {
            "id": appt.id,
            "patientid": appt.patientid,
            "doctorid": appt.doctorid,
            "appointmentdate": appt.appointmentdate,
            "appointmenttime": appt.appointmenttime.strftime("%H:%M"),
            "reason": appt.reason,
            "status": appt.status,
        }
        result.append(apptdict)

    return result


@router.get("/appointments/upcoming")
async def getupcomingappointments(db: Session = Depends(getdb)):
    """Get upcoming appointments"""
    today = date.today()
    appointments = (
        db.query(Appointment)
        .filter(Appointment.appointmentdate >= today, Appointment.status == "scheduled")
        .order_by(Appointment.appointmentdate, Appointment.appointmenttime)
        .limit(10)
        .all()
    )

    result = []
    for appt in appointments:
        patient = db.query(Patient).filter(Patient.id == appt.patientid).first()
        doctor = db.query(Doctor).filter(Doctor.id == appt.doctorid).first()

        result.append(
            {
                "id": appt.id,
                "patientname": patient.name if patient else "Unknown",
                "doctorname": doctor.name if doctor else "Unknown",
                "date": appt.appointmentdate.strftime("%Y-%m-%d"),
                "time": appt.appointmenttime.strftime("%H:%M"),
                "reason": appt.reason,
                "status": appt.status,
            }
        )

    return result


@router.get("/appointments/today")
async def gettodayappointments(db: Session = Depends(getdb)):
    """Get today's appointments"""
    today = date.today()
    appointments = (
        db.query(Appointment)
        .filter(Appointment.appointmentdate == today, Appointment.status == "scheduled")
        .order_by(Appointment.appointmenttime)
        .all()
    )

    result = []
    for appt in appointments:
        patient = db.query(Patient).filter(Patient.id == appt.patientid).first()
        doctor = db.query(Doctor).filter(Doctor.id == appt.doctorid).first()

        result.append(
            {
                "id": appt.id,
                "patientname": patient.name if patient else "Unknown",
                "doctorname": doctor.name if doctor else "Unknown",
                "time": appt.appointmenttime.strftime("%H:%M"),
                "reason": appt.reason,
            }
        )

    return result


# Calls
@router.get("/calls", response_model=List[CallResponse])
async def getcalls(skip: int = 0, limit: int = 50, db: Session = Depends(getdb)):
    """Get recent calls"""
    calls = db.query(Call).order_by(Call.starttime.desc()).offset(skip).limit(limit).all()
    return calls


@router.get("/calls/{callid}")
async def getcall(callid: int, db: Session = Depends(getdb)):
    """Get call details"""
    call = db.query(Call).filter(Call.id == callid).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    # Parse transcript
    messages = []
    if call.transcript:
        for line in call.transcript.split("\n"):
            if ":" in line:
                role, content = line.split(":", 1)
                messages.append({"role": role.strip().lower(), "content": content.strip()})

    return {
        "id": call.id,
        "callername": call.callername,
        "starttime": call.starttime,
        "endtime": call.endtime,
        "duration": call.duration,
        "intent": call.intent,
        "status": call.status,
        "emergencydetected": call.emergencydetected,
        "transcript": messages,
    }


@router.get("/calls/emergency")
async def getemergencycalls(db: Session = Depends(getdb)):
    """Get emergency calls"""
    calls = (
        db.query(Call).filter(Call.emergencydetected == True).order_by(Call.starttime.desc()).limit(20).all()
    )

    return [
        {"id": c.id, "callername": c.callername, "starttime": c.starttime, "intent": c.intent, "status": c.status}
        for c in calls
    ]


# Analytics
@router.get("/analytics")
async def getanalytics(db: Session = Depends(getdb)):
    """Get analytics dashboard data"""
    today = date.today()
    weekago = today - timedelta(days=7)
    monthago = today - timedelta(days=30)

    # Total patients
    totalpatients = db.query(Patient).count()

    # Appointments stats
    totalappointments = db.query(Appointment).count()
    upcomingappointments = (
        db.query(Appointment).filter(Appointment.appointmentdate >= today, Appointment.status == "scheduled").count()
    )
    todayappointments = db.query(Appointment).filter(Appointment.appointmentdate == today).count()

    # Calls stats
    totalcalls = db.query(Call).count()
    callstoday = db.query(Call).filter(Call.starttime >= datetime.combine(today, datetime.min.time())).count()
    callsweek = db.query(Call).filter(Call.starttime >= datetime.combine(weekago, datetime.min.time())).count()
    emergencycalls = db.query(Call).filter(Call.emergencydetected == True).count()

    # Average call duration
    durations = [c.duration for c in db.query(Call).filter(Call.duration != None).all() if c.duration]
    avgduration = sum(durations) / len(durations) if durations else 0

    # Intent distribution
    intents = db.query(Call.intent, func.count(Call.id)).group_by(Call.intent).all()
    intentdistribution = {intent: count for intent, count in intents if intent}

    return {
        "patients": {"total": totalpatients},
        "appointments": {"total": totalappointments, "upcoming": upcomingappointments, "today": todayappointments},
        "calls": {"total": totalcalls, "today": callstoday, "week": callsweek, "emergency": emergencycalls, "avgduration": int(avgduration)},
        "intentdistribution": intentdistribution,
    }


# Medical Knowledge
@router.get("/knowledge/search")
async def searchknowledge(query: str, db: Session = Depends(getdb)):
    """Search medical knowledge base"""
    results = (
        db.query(MedicalKnowledge)
        .filter(MedicalKnowledge.term.ilike(f"%{query}%") | MedicalKnowledge.description.ilike(f"%{query}%"))
        .limit(5)
        .all()
    )

    return [
        {"id": k.id, "category": k.category, "term": k.term, "description": k.description, "severity": k.severity}
        for k in results
    ]