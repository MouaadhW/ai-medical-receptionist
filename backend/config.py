from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APPNAME: str = "AI Medical Receptionist"
    CLINICNAME: str = "HealthCare Clinic"
    VERSION: str = "1.0.0"
    SECRET_KEY: str = "supersecretkey123"  # In production, use env variable
    
    # Server
    APIHOST: str = "0.0.0.0"
    APIPORT: int = 8000
    VOICEPORT: int = 8003
    
    # Database
    DATABASEURL: str = "sqlite:///./medicalreceptionist.db"
    
    # LLM Configuration
    LLMPROVIDER: str = "ollama"
    LLMMODEL: str = "llama3.1:8b"  # Optimal for medical conversations
    LLMTEMPERATURE: float = 0.7
    LLMMAXTOKENS: int = 150
    
    # MIMIC-IV Configuration
    MIMICDATAPATH: str = "./mimicdata"
    ENABLEMEDICALQA: bool = True
    
    # Emergency Keywords
    EMERGENCYKEYWORDS: list = [
        "chest pain", "heart attack", "stroke", "can't breathe",
        "severe bleeding", "unconscious", "seizure", "overdose",
        "severe pain", "emergency", "911", "ambulance"
    ]
    
    # Appointment Settings
    APPOINTMENTDURATIONMINUTES: int = 30
    CLINICHOURSSTART: str = "08:00"
    CLINICHOURSEND: str = "17:00"
    CLINICDAYS: list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # Voice Settings
    SPEECHRATE: float = 1.2  # 20% faster
    ENABLEVOICERECORDING: bool = True

    # Email Settings (SMTP)
    SMTPSERVER: str = "smtp.gmail.com"  # e.g., smtp.gmail.com, smtp.sendgrid.net
    SMTPPORT: int = 587
    SMTPUSERNAME: str = "your-email@gmail.com"
    SMTPPASSWORD: str = "your-app-password"
    SENDEREMAIL: str = "noreply@medpulse.com"
    ENABLEEMAILNOTIFICATIONS: bool = True
    
    class Config:
        envfile = ".env"

config = Settings()