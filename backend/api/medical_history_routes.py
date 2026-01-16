"""
Medical History API Routes - FastAPI endpoints for Neural History module
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import secrets

from db.database import getdb
from db.medical_history import MedicalEvent, AnatomicalLocation, AIInsight, SharedVault
from db.models import Patient
from services.ai_insights_service import ai_insights_service
from services.encryption_service import encryption_service

router = APIRouter(prefix="/api/history", tags=["medical_history"])


# Get complete medical timeline for patient
@router.get("/patient/{patient_id}")
def get_patient_history(patient_id: int, db: Session = Depends(getdb)):
    """Get complete medical timeline for a patient"""
    try:
        events = db.query(MedicalEvent).filter(
            MedicalEvent.patient_id == patient_id
        ).order_by(MedicalEvent.event_date.desc()).all()

        return {
            "patient_id": patient_id,
            "events": events,
            "total_count": len(events),
            "severity_breakdown": {
                "critical": len([e for e in events if e.severity == "critical"]),
                "high": len([e for e in events if e.severity == "high"]),
                "medium": len([e for e in events if e.severity == "medium"]),
                "low": len([e for e in events if e.severity == "low"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Create new medical event
@router.post("/events/create")
def create_medical_event(
    patient_id: int,
    event_type: str,
    title: str,
    description: str,
    event_date: str,
    severity: str = "low",
    status: str = "active",
    provider_name: Optional[str] = None,
    facility_name: Optional[str] = None,
    anatomical_locations: Optional[List[str]] = None,
    db: Session = Depends(getdb)
):
    """Create a new medical event for a patient"""
    try:
        from datetime import datetime
        
        # Create medical event
        event = MedicalEvent(
            patient_id=patient_id,
            event_type=event_type,
            title=title,
            description=description,
            event_date=datetime.fromisoformat(event_date.replace('Z', '+00:00')),
            severity=severity,
            status=status,
            provider_name=provider_name,
            facility_name=facility_name
        )
        db.add(event)
        db.flush()  # Get the event ID
        
        # Add anatomical locations if provided
        if anatomical_locations:
            for location in anatomical_locations:
                anatom_loc = AnatomicalLocation(
                    medical_event_id=event.id,
                    body_region=location
                )
                db.add(anatom_loc)
        
        db.commit()
        db.refresh(event)
        
        return {
            "success": True,
            "event": event,
            "message": "Medical event created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Get events grouped by anatomical location
@router.get("/anatomical/{patient_id}")
def get_history_by_anatomy(patient_id: int, db: Session = Depends(getdb)):
    """Get medical events grouped by body region for 3D visualization"""
    try:
        # Get all events with their anatomical locations
        events = db.query(MedicalEvent).filter(
            MedicalEvent.patient_id == patient_id
        ).all()

        # Group by body region
        anatomical_map = {}
        for event in events:
            locations = db.query(AnatomicalLocation).filter(
                AnatomicalLocation.medical_event_id == event.id
            ).all()

            for loc in locations:
                region = loc.body_region
                if region not in anatomical_map:
                    anatomical_map[region] = []
                
                anatomical_map[region].append({
                    "event": event,
                    "location_details": {
                        "body_system": loc.body_system,
                        "specific_location": loc.specific_location,
                        "laterality": loc.laterality
                    }
                })

        return {
            "patient_id": patient_id,
            "anatomical_map": anatomical_map,
            "regions_affected": list(anatomical_map.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Generate AI insights for a medical event
@router.post("/insights/generate")
def generate_insights(event_id: int, db: Session = Depends(getdb)):
    """Generate AI-powered insights for a medical event"""
    try:
        event = db.query(MedicalEvent).filter(MedicalEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Medical event not found")

        event_data = {
            "event_type": event.event_type,
            "title": event.title,
            "description": event.description,
            "event_date": str(event.event_date),
            "severity": event.severity,
            "status": event.status
        }

        # Generate different types of insights
        insights_generated = []

        # Key takeaway
        takeaway = ai_insights_service.generate_medical_event_summary(event_data)
        insight_takeaway = AIInsight(
            medical_event_id=event_id,
            insight_type="key_takeaway",
            content=takeaway,
            confidence_score=0.85
        )
        db.add(insight_takeaway)
        insights_generated.append(insight_takeaway)

        # Follow-up recommendation
        if event.status in ["active", "follow_up_needed"]:
            recommendation = ai_insights_service.generate_follow_up_recommendation(event_data)
            insight_recommendation = AIInsight(
                medical_event_id=event_id,
                insight_type="recommendation",
                content=recommendation,
                confidence_score=0.80
            )
            db.add(insight_recommendation)
            insights_generated.append(insight_recommendation)

        db.commit()

        return {
            "event_id": event_id,
            "insights_generated": len(insights_generated),
            "insights": insights_generated
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Create secure sharing vault
@router.post("/share/create")
def create_sharing_vault(
    patient_id: int,
    event_ids: List[int],
    recipient_name: str,
    recipient_email: str,
    expiry_hours: int = 48,
    db: Session = Depends(getdb)
):
    """Create secure vault for sharing medical history with 2FA"""
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Verify all events belong to this patient
        for event_id in event_ids:
            event = db.query(MedicalEvent).filter(
                MedicalEvent.id == event_id,
                MedicalEvent.patient_id == patient_id
            ).first()
            if not event:
                raise HTTPException(
                    status_code=400,
                    detail=f"Event {event_id} not found or doesn't belong to patient"
                )

        # Create secure vault
        vault_data = encryption_service.create_secure_vault(
            patient_id,
            event_ids,
            recipient_email,
            expiry_hours
        )

        # Save to database
        vault = SharedVault(
            patient_id=patient_id,
            vault_token=vault_data["vault_token"],
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            shared_events=event_ids,
            two_fa_code=vault_data["two_fa_code"],
            two_fa_method="email",
            expires_at=datetime.fromisoformat(vault_data["expires_at"]),
            access_log=[]
        )
        db.add(vault)
        db.commit()

        return {
            "vault_url": f"/vault/{vault_data['vault_token']}",
            "vault_token": vault_data["vault_token"],
            "two_fa_sent_to": recipient_email,
            "expires_at": vault_data["expires_at"],
            "expiry_hours": expiry_hours,
            "events_shared": len(event_ids),
            "message": f"Secure vault created. 2FA code sent to {recipient_email}"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Access shared vault
@router.get("/share/{vault_token}")
def get_shared_vault(vault_token: str, db: Session = Depends(getdb)):
    """Get shared vault metadata (before 2FA verification)"""
    try:
        vault = db.query(SharedVault).filter(
            SharedVault.vault_token == vault_token,
            SharedVault.is_active == True
        ).first()

        if not vault:
            raise HTTPException(status_code=404, detail="Vault not found or expired")

        # Check if expired
        if datetime.now() > vault.expires_at:
            vault.is_active = False
            db.commit()
            raise HTTPException(status_code=410, detail="Vault has expired")

        # Check access limit
        if vault.access_count >= vault.max_access_count:
            vault.is_active = False
            db.commit()
            raise HTTPException(status_code=403, detail="Maximum access attempts exceeded")

        return {
            "vault_token": vault_token,
            "recipient_name": vault.recipient_name,
            "two_fa_required": True,
            "two_fa_method": vault.two_fa_method,
            "expires_at": vault.expires_at.isoformat(),
            "events_count": len(vault.shared_events),
            "message": "Please enter 2FA code to access medical records"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Verify 2FA and access vault content
@router.post("/share/verify")
def verify_vault_access(
    vault_token: str,
    two_fa_code: str,
    request: Request,
    db: Session = Depends(getdb)
):
    """Verify 2FA code and grant access to vault contents"""
    try:
        vault = db.query(SharedVault).filter(
            SharedVault.vault_token == vault_token,
            SharedVault.is_active == True
        ).first()

        if not vault:
            raise HTTPException(status_code=404, detail="Vault not found")

        # Verify 2FA code
        if not encryption_service.verify_vault_access(vault_token, two_fa_code, vault.two_fa_code):
            # Log failed attempt
            vault.access_count += 1
            db.commit()
            raise HTTPException(status_code=401, detail="Invalid 2FA code")

        # Access granted - log access
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        access_entry = encryption_service.create_access_log_entry(
            vault_token,
            client_ip,
            user_agent
        )

        access_log = vault.access_log or []
        access_log.append(access_entry)
        vault.access_log = access_log
        vault.access_count += 1
        vault.last_accessed_at = datetime.now()
        db.commit()

        # Get shared medical events
        events = db.query(MedicalEvent).filter(
            MedicalEvent.id.in_(vault.shared_events)
        ).all()

        # Get insights for each event
        events_with_insights = []
        for event in events:
            insights = db.query(AIInsight).filter(
                AIInsight.medical_event_id == event.id
            ).all()

            anatomical_locs = db.query(AnatomicalLocation).filter(
                AnatomicalLocation.medical_event_id == event.id
            ).all()

            events_with_insights.append({
                "event": event,
                "insights": insights,
                "anatomical_locations": anatomical_locs
            })

        return {
            "access_granted": True,
            "patient_id": vault.patient_id,
            "events": events_with_insights,
            "shared_by": "MedPulse Clinic",
            "expires_at": vault.expires_at.isoformat(),
            "read_only": True,
            "watermark": "Shared Medical Record - Confidential"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Revoke vault access
@router.post("/share/revoke/{vault_token}")
def revoke_vault_access(vault_token: str, patient_id: int, db: Session = Depends(getdb)):
    """Revoke access to a shared vault"""
    try:
        vault = db.query(SharedVault).filter(
            SharedVault.vault_token == vault_token,
            SharedVault.patient_id == patient_id
        ).first()

        if not vault:
            raise HTTPException(status_code=404, detail="Vault not found")

        vault.is_active = False
        db.commit()

        return {
            "vault_token": vault_token,
            "status": "revoked",
            "message": "Vault access has been revoked"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
