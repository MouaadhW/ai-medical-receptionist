# 🏥 AI Medical Receptionist System

An intelligent, HIPAA-compliant AI receptionist for medical clinics with emergency detection, appointment scheduling, doctor management, and comprehensive urgent care guidance.

## ✨ Features

### Core Capabilities
- 🚨 **Emergency Detection** - Automatic triage for critical situations with immediate 911 protocols
- 📅 **Smart Scheduling** - Appointment booking with doctor preference and availability checking
- �‍⚕️ **Doctor Management** - **NEW** Admin interface to manage medical staff and schedules
- 📞 **Modern Voice Interface** - Real-time speech-to-text with conversational AI
- 📊 **Analytics Dashboard** - Beautiful, modern visualizations of clinic metrics
- 📜 **Call Transcripts** - **NEW** Full history and transcripts of all patient interactions
- 🔒 **HIPAA Compliant** - Secure patient data handling and specialized authentication

### **Advanced Urgent Care System** 🏥
- **8-Step Triage Process** - Professional assessment protocol for accurate advice
- **Medical Knowledge Base** - Sourced from CDC, Mayo Clinic, and Red Cross
- **Conditions Covered** - Guidance for 12+ scenarios (Burns, Fevers, Cuts, Chest Pain)
- **First-Aid Instructions** - Step-by-step medically-advised procedures

---

## ⚡ Quick Start (Docker - Recommended)

Everything is containerized for easy deployment.

### Prerequisites
- **Docker Desktop** installed and running

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MouaadhW/ai-medical-receptionist
   cd ai-medical-receptionist
   ```

2. **Run the System:**
   ```bash
   docker-compose up --build
   ```
   *Note: First run downloads the 5GB LLM model. It may take some time.*

3. **Access the Application:**
   - **Modern Dashboard:** [http://localhost:3000](http://localhost:3000)
   - **Voice Interface:** [http://localhost:3000/phone](http://localhost:3000/phone)
   - **Backend API:** [http://localhost:8000/docs](http://localhost:8000/docs)

**Default Login:**
- Username: `admin`
- Password: `password`

---

## 📱 User Guide

### 1. Dashboard & Analytics
The revamped **Admin Dashboard** provides a holistic view of the clinic:
- **Stats Overview**: Today's appointments, patients, and emergencies.
- **Charts**: Visual distribution of appointment types and urgencies.
- **Quick Actions**: Easy navigation to manage doctors or patients.

### 2. Managing Doctors (New!)
Navigate to the **Doctors** page to:
- **Add New Doctors:** Create profiles with specialties (Cardiology, Pediatrics, etc.).
- **View Roster:** See all registered medical staff in a clean, searchable table.
- **Schedule Management:** (Upcoming) Manage doctor shifts.

### 3. Call History & Transcripts
The **Calls** page offers meaningful insights:
- **Live Updates:** See incoming calls in real-time.
- **Transcripts:** Click any call to read the full conversation text.
- **Intent Analysis:** Automatic classification (Emergency vs Appointment vs Info).

### 4. Voice Interaction
Navigate to **Voice Test** (or `/phone`):
- Click **"Start Call"** and speak naturally.
- Examples:
  - *"I need to see a doctor for a headache."* (Booking)
  - *"My chest hurts badly."* (Emergency Triage)
  - *"How do I treat a burn?"* (Medical Advice)

---

## 🗂️ Project Structure

```
ai-medical-receptionist/
├── backend/
│   ├── agent/                 # AI Logic (LangGraph/LangChain)
│   │   ├── medical_agent.py   # Core Agent & Appointment Logic
│   │   └── emergency_detector.py
│   ├── api/                   # FastAPI Endpoints
│   ├── db/                    # SQLite Database & Models
│   ├── mimic/                 # Knowledge Base Data
│   ├── scripts/               # Utility scripts (Seeding, Debugging)
│   ├── voice/                 # Whisper & TTS Server
│   └── main.py                # App Entry Point
├── frontend/
│   ├── src/
│   │   ├── components/        # React Components
│   │   │   ├── Doctors.js     # ⭐ Doctor Management
│   │   │   ├── Calls.js       # ⭐ Call History & Transcripts
│   │   │   ├── Dashboard.js   # Analytics
│   │   │   ├── DoctorDashboard.js # Individual Doctor View
│   │   │   └── ...
│   │   ├── App.css            # Global Modern Theme
│   │   └── theme.css          # Design System Variables
│   └── public/
├── docker-compose.yml         # Container Orchestration
└── README.md                  # Documentation
```

---

## 🔧 Configuration

**Environment Variables (`.env`)**:
Customize the clinic's operation:
```env
CLINIC_NAME=MedPulse Clinic
CLINIC_HOURS_START=08:00
CLINIC_HOURS_END=17:00
LLM_MODEL=llama3.1:8b
# See .env.example for full list
```

---

## 🔒 Security & Compliance
- **Patient Verification:** Uses "Special Key" authentication (e.g., `SMITH1985`).
- **Data Protection:** No PHI Logging, standard encryption.
- **Role-Based Access:** Admin vs Doctor vs Patient views.

---

## ⚠️ Medical Disclaimer
This AI system is for **educational and administrative assistance** only.
- **NOT** a replacement for professional medical advice.
- **Call 911** immediately in emergencies.
- Follows official guidance (CDC/Mayo Clinic) but should not be used for diagnosis.

---

**Built with ❤️ for Healthcare Innovation**
*v2.1 - Enhanced UI & Doctor Management*