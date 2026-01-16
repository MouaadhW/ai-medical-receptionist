"""
Billing API Routes - FastAPI endpoints for Pulse Ledger module
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import secrets

from db.database import getdb
from db.billing import Bill, BillItem, Payment, InsuranceClaim, CostPrediction
from db.models import Patient
from services.ai_insights_service import ai_insights_service
from services.payment_service import payment_service

router = APIRouter(prefix="/api/billing", tags=["billing"])


# Get all bills for a patient
@router.get("/patient/{patient_id}")
def get_patient_bills(patient_id: int, db: Session = Depends(getdb)):
    """Get all bills for a specific patient"""
    try:
        bills = db.query(Bill).filter(Bill.patient_id == patient_id).all()
        return {
            "patient_id": patient_id,
            "bills": bills,
            "total_count": len(bills)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get detailed bill breakdown with AI explanations
@router.get("/{bill_id}/details")
def get_bill_details(bill_id: int, db: Session = Depends(getdb)):
    """Get itemized bill breakdown with AI explanations"""
    try:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")

        # Get bill items
        items = db.query(BillItem).filter(BillItem.bill_id == bill_id).all()
        
        # Generate AI explanations for items without them
        for item in items:
            if not item.ai_explanation:
                item.ai_explanation = ai_insights_service.generate_bill_explanation(
                    item.description,
                    item.category,
                    f"Bill #{bill.bill_number}"
                )
                db.commit()

        return {
            "bill": bill,
            "items": items,
            "summary": {
                "total_amount": bill.total_amount,
                "insurance_covered": bill.insurance_covered,
                "patient_due": bill.patient_due,
                "status": bill.status
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Generate cost prediction for next visit
@router.post("/predict")
def predict_cost(patient_id: int, visit_type: str, db: Session = Depends(getdb)):
    """Generate AI-powered cost prediction for future visit"""
    try:
        # Get patient's billing history
        past_bills = db.query(Bill).filter(Bill.patient_id == patient_id).all()
        history = [{"total": b.total_amount, "type": "general"} for b in past_bills]

        # Generate prediction
        prediction = ai_insights_service.predict_visit_cost(history, visit_type)
        
        # Save prediction to database
        cost_pred = CostPrediction(
            patient_id=patient_id,
            predicted_visit_type=visit_type,
            predicted_min_cost=prediction["min_cost"],
            predicted_max_cost=prediction["max_cost"],
            predicted_avg_cost=prediction["avg_cost"],
            confidence_level=prediction["confidence"],
            breakdown=prediction["breakdown"],
            valid_until=datetime.now() + timedelta(days=30)
        )
        db.add(cost_pred)
        db.commit()

        return {
            "prediction": prediction,
            "valid_until": cost_pred.valid_until,
            "note": "Prediction based on historical billing data and clinic averages"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Process payment
@router.post("/payment/process")
def process_payment(
    bill_id: int,
    payment_method: str,  # d17, flouci, cnam, cash, card
    amount: float,
    db: Session = Depends(getdb)
):
    """Process payment through selected gateway"""
    try:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")

        patient = db.query(Patient).filter(Patient.id == bill.patient_id).first()
        patient_info = {"name": patient.name, "phone": patient.phone, "email": patient.email}

        # Route to appropriate payment gateway
        result = None
        if payment_method == "d17":
            result = payment_service.process_d17_payment(amount, bill_id, patient_info)
        elif payment_method == "flouci":
            result = payment_service.process_flouci_payment(amount, bill_id, patient_info)
        elif payment_method in ["cash", "card"]:
            # Direct payment - create transaction record
            result = {
                "status": "completed",
                "transaction_id": f"{payment_method.upper()}-{secrets.token_hex(8).upper()}",
                "amount": amount,
                "message": f"{payment_method.title()} payment recorded"
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid payment method")

        # Create payment record
        payment = Payment(
            bill_id=bill_id,
            amount=amount,
            payment_method=payment_method,
            payment_gateway=payment_method if payment_method in ["d17", "flouci"] else None,
            transaction_id=result.get("transaction_id"),
            status=result.get("status", "pending"),
            gateway_response=result
        )
        db.add(payment)

        # Update bill status if fully paid
        if payment.status == "completed":
            bill.patient_due -= amount
            if bill.patient_due <= 0:
                bill.status = "paid"
                bill.paid_date = datetime.now()

        db.commit()

        return {
            "payment": payment,
            "gateway_response": result,
            "bill_status": bill.status
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Check insurance status
@router.get("/insurance/status/{patient_id}")
def get_insurance_status(patient_id: int, db: Session = Depends(getdb)):
    """Check patient's CNAM insurance coverage status"""
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Get insurance info (mock for now)
        insurance_id = patient.insuranceinfo or f"CNAM-{patient_id:06d}"
        status = payment_service.check_cnam_status(insurance_id)

        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Submit insurance claim
@router.post("/insurance/claim")
def submit_insurance_claim(bill_id: int, db: Session = Depends(getdb)):
    """Submit CNAM insurance claim for a bill"""
    try:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")

        patient = db.query(Patient).filter(Patient.id == bill.patient_id).first()
        patient_info = {"name": patient.name, "insurance_id": patient.insuranceinfo}

        # Get bill items
        items_data = []
        items = db.query(BillItem).filter(BillItem.bill_id == bill_id).all()
        for item in items:
            items_data.append({
                "description": item.description,
                "category": item.category,
                "total_price": item.total_price
            })

        # Submit claim
        result = payment_service.submit_cnam_claim(bill_id, patient_info, items_data)

        # Create insurance claim record
        claim = InsuranceClaim(
            bill_id=bill_id,
            patient_id=bill.patient_id,
            claim_number=result["claim_number"],
            insurance_provider="CNAM",
            claim_amount=result["claim_amount"],
            approved_amount=result.get("expected_coverage", 0),
            status="submitted"
        )
        db.add(claim)

        # Update bill with insurance coverage estimate
        bill.insurance_covered = result.get("expected_coverage", 0)
        bill.patient_due = bill.total_amount - bill.insurance_covered

        db.commit()

        return {
            "claim": claim,
            "result": result,
            "updated_bill": {
                "insurance_covered": bill.insurance_covered,
                "patient_due": bill.patient_due
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Get cost vs value transparency analysis
@router.get("/transparency/{bill_id}")
def get_cost_transparency(bill_id: int, db: Session = Depends(getdb)):
    """Get cost vs. value transparency analysis"""
    try:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")

        bill_data = {"total_amount": bill.total_amount}
        analysis = ai_insights_service.analyze_cost_vs_value(bill_data)

        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
