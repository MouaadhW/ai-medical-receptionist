from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.database import getdb
from db.models import Patient, Doctor, Appointment, Call, MedicalKnowledge, User, TempCall
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    require_role,
)
from datetime import date, datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import random
import string

# Import new route modules
from api.billing_routes import router as billing_router
from api.medical_history_routes import router as medical_history_router

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


# Auth Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class CreateDoctorRequest(BaseModel):
    name: str
    username: str
    email: str
    password: str
    specialty: str
    phone: str
    availabledays: str = "Mon,Tue,Wed,Thu,Fri"


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    otid: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    otid: str
    created_at: datetime

    class Config:
        orm_mode = True


# --- Authentication Routes ---

@router.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(getdb)):
    """Register a new user"""
    # Check if user exists
    db_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    # Generate OTID (5 digit unique code)
    while True:
        otid = "".join(random.choices(string.digits, k=5))
        if not db.query(User).filter(User.otid == otid).first():
            break

    # Create user
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role="user",  # Default role
        otid=otid,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(getdb)):
    """Login user"""
    # Case-insensitive username lookup
    user = db.query(User).filter(func.lower(User.username) == func.lower(form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role, "otid": user.otid})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,
        "otid": user.otid
    }


@router.get("/auth/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


# --- Admin Routes ---

@router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(require_role("admin")), # Enforce Admin Role
    db: Session = Depends(getdb)
):
    """Get all users (Admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int, 
    current_user: User = Depends(require_role("admin")), 
    db: Session = Depends(getdb)
):
    """Delete a user (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# --- Existing Routes (with optional updates if needed) ---

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
    # For now, allowing public access or you can verify user here
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

    # Fix: Ensure all datetime objects are properly handled
    from datetime import datetime as dt_class

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
    ]# ==== DOCTOR SPECIFIC ENDPOINTS ====

@router.get("/doctor/my-schedule")
async def get_doctor_schedule(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(getdb)
):
    """Get appointments for the logged-in doctor"""
    # 1. Find the Doctor profile linked to this user
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=403, detail="User is not a doctor")
    
    # 2. Get appointments
    appointments = db.query(Appointment).filter(
        Appointment.doctorid == doctor.id
    ).order_by(Appointment.appointmentdate.asc(), Appointment.appointmenttime.asc()).all()
    
    # 3. Format response with Patient info
    result = []
    for appt in appointments:
        patient_name = "Unknown"
        if appt.patient:
            patient_name = appt.patient.name
        elif appt.user and appt.user.patient:
             patient_name = appt.user.patient.name
        
        result.append({
            "id": appt.id,
            "patient_name": patient_name,
            "date": appt.appointmentdate.isoformat(),
            "time": appt.appointmenttime.strftime("%H:%M"),
            "reason": appt.reason,
            "status": appt.status,
            "notes": appt.notes
        })
    return result


@router.post("/admin/create-doctor", response_model=UserResponse)
async def create_doctor_account(
    req: CreateDoctorRequest, 
    current_user: User = Depends(require_role("admin")), 
    db: Session = Depends(getdb)
):
    """Create a new Doctor account and profile (Admin only)"""
    # 1. Check if user exists
    if db.query(User).filter((User.username == req.username) | (User.email == req.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # 2. Generate OTID
    while True:
        otid = "".join(random.choices(string.digits, k=5))
        if not db.query(User).filter(User.otid == otid).first():
            break

    # 3. Create User Account (Role="doctor")
    hashed_password = get_password_hash(req.password)
    new_user = User(
        username=req.username,
        email=req.email,
        hashed_password=hashed_password,
        role="doctor",
        otid=otid,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 4. Create Doctor Profile linked to User
    new_doctor = Doctor(
        name=req.name,
        specialty=req.specialty,
        phone=req.phone,
        email=req.email,
        availabledays=req.availabledays,
        user_id=new_user.id
    )
    db.add(new_doctor)
    db.commit()
    
    return new_user


@router.get("/doctors")
async def get_all_doctors(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(getdb)
):
    """List all doctors (Admin only)"""
    doctors = db.query(Doctor).all()
    return [{
        "id": d.id, 
        "name": d.name, 
        "specialty": d.specialty, 
        "email": d.email,
        "phone": d.phone,
        "username": d.user.username if d.user else "N/A"
    } for d in doctors]

# Get current user's appointments
@router.get("/my-appointments")
async def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(getdb)
):
    """Get all appointments for the logged-in user"""
    # Robust query: match by UserID OR PatientID (if linked)
    query_filter = (Appointment.userid == current_user.id)
    if current_user.patient:
        query_filter = (Appointment.userid == current_user.id) | (Appointment.patientid == current_user.patient.id)
    
    appointments = db.query(Appointment).filter(
        query_filter
    ).order_by(Appointment.appointmentdate.desc(), Appointment.appointmenttime.desc()).all()
    
    result = []
    for appt in appointments:
        # Get doctor info
        doctor = db.query(Doctor).filter(Doctor.id == appt.doctorid).first()
        
        appt_dict = {
            "id": appt.id,
            "doctor_name": f"Dr. {doctor.name}" if doctor else "Unknown",
            "specialty": doctor.specialty if doctor else "General",
            "appointment_date": appt.appointmentdate.isoformat(),
            "appointment_time": appt.appointmenttime.strftime("%H:%M"),
            "duration_minutes": appt.durationminutes,
            "reason": appt.reason,
            "status": appt.status,
            "notes": appt.notes,
            "created_at": appt.createdat.isoformat() if appt.createdat else None
        }
        result.append(appt_dict)
    
    return result


# ==== ADMIN APPOINTMENT MANAGEMENT ====

# Get all appointments (admin only)
@router.get("/admin/appointments/all")
async def get_all_appointments_admin(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(getdb),
    skip: int = 0,
    limit: int = 100
):
    """Get all appointments with user and doctor details (admin only)"""
    appointments = db.query(Appointment).order_by(
        Appointment.appointmentdate.desc(),
        Appointment.appointmenttime.desc()
    ).offset(skip).limit(limit).all()
    
    result = []
    for appt in appointments:
        user = db.query(User).filter(User.id == appt.userid).first() if appt.userid else None
        doctor = db.query(Doctor).filter(Doctor.id == appt.doctorid).first()
        patient = db.query(Patient).filter(Patient.id == appt.patientid).first() if appt.patientid else None
        
        appt_dict = {
            "id": appt.id,
            "user_id": appt.userid,
            "user_name": user.username if user else (patient.name if patient else "Unknown"),
            "user_email": user.email if user else (patient.email if patient else "N/A"),
            "doctor_id": appt.doctorid,
            "doctor_name": f"Dr. {doctor.name}" if doctor else "Unknown",
            "specialty": doctor.specialty if doctor else "General",
            "appointment_date": appt.appointmentdate.isoformat(),
            "appointment_time": appt.appointmenttime.strftime("%H:%M"),
            "duration_minutes": appt.durationminutes,
            "reason": appt.reason,
            "status": appt.status,
            "notes": appt.notes,
            "created_at": appt.createdat.isoformat() if appt.createdat else None,
            "updated_at": appt.updatedat.isoformat() if appt.updatedat else None
        }
        result.append(appt_dict)
    
    return result


# Update appointment (admin only)
@router.put("/admin/appointments/{appointment_id}")
async def update_appointment_admin(
    appointment_id: int,
    appointment_date: Optional[str] = None,
    appointment_time: Optional[str] = None,
    status: Optional[str] = None,
    notes: Optional[str] = None,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(getdb)
):
    """Update an appointment (admin only)"""
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment_date:
        from datetime import datetime as dt
        appt.appointmentdate = dt.fromisoformat(appointment_date).date()
    
    if appointment_time:
        from datetime import datetime as dt
        appt.appointmenttime = dt.strptime(appointment_time, "%H:%M").time()
    
    if status:
        appt.status = status
    
    if notes is not None:
        appt.notes = notes
    
    appt.updatedat = datetime.now()
    db.commit()
    db.refresh(appt)
    
    return {"message": "Appointment updated successfully", "id": appt.id}


# Delete appointment (admin only)
@router.delete("/admin/appointments/{appointment_id}")
async def delete_appointment_admin(
    appointment_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(getdb)
):
    """Delete an appointment (admin only)"""
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db.delete(appt)
    db.commit()
    
    return {"message": "Appointment deleted successfully", "id": appointment_id}
