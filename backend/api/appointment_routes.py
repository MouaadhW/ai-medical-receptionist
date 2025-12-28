# ==== USER APPOINTMENT ENDPOINTS ====

# Get current user's appointments
@router.get("/my-appointments")
async def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(getdb)
):
    """Get all appointments for the logged-in user"""
    appointments = db.query(Appointment).filter(
        Appointment.userid == current_user.id
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
    
    old_status = appt.status
    old_date = appt.appointmentdate
    old_time = appt.appointmenttime
    
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

    # Trigger Email Notification
    try:
        if appt.userid:
            user = db.query(User).filter(User.id == appt.userid).first()
            if user and user.email:
                from services.email_service import email_service
                email_service.send_appointment_update(
                    user.email,
                    user.username,
                    appt.appointmentdate.strftime("%Y-%m-%d"),
                    appt.appointmenttime.strftime("%H:%M"),
                    appt.status
                )
    except Exception as e:
        print(f"Error triggering email: {e}")
    
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
    
    # Store needed info before deletion
    appt_date = appt.appointmentdate
    appt_time = appt.appointmenttime
    user_id = appt.userid
    
    db.delete(appt)
    db.commit()
    
    # Trigger Email Notification
    try:
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.email:
                from services.email_service import email_service
                email_service.send_appointment_cancellation(
                    user.email,
                    user.username,
                    appt_date.strftime("%Y-%m-%d"),
                    appt_time.strftime("%H:%M")
                )
    except Exception as e:
        print(f"Error triggering email: {e}")
    
    return {"message": "Appointment deleted successfully", "id": appointment_id}
