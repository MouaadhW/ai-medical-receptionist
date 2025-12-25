# Project Organization Script
# This file documents the final organized structure

## Files to Keep

### Root Directory
- .env                      # Environment configuration
- .env.example              # Environment template
- README.md                 # Main documentation
- docker-compose.yml        # Docker orchestration
- start.bat                 # Windows startup script
- start.sh                  # Linux/Mac startup script

###Backend Directory(/backend)
├── agent/                  # AI Agent Logic
│   ├── __init__.py
│   ├── emergency_detector.py
│   ├── intent_classifier.py
│   ├── knowledge_base.py
│   └── medical_agent.py
├── api/                    # FastAPI Backend
│   ├── __init__.py
│   ├── routes.py
│   └── server.py
├── db/                     # Database Layer
│   ├── __init__.py
│   ├── database.py
│   ├── init_db.py
│   ├── models.py
│   └── medicalreceptionist.db  # ⚠️ SHOULD BE HERE (currently in backend/)
├── mimic/                  # Medical Knowledge
│   ├── __init__.py
│   ├── medical_qa.py
│   ├── mimic_loader.py
│   ├── urgent_care_handler.py   # ✅ NEW
│   └── urgent_care_knowledge.py # ✅ NEW
├── voice/                  # Voice Interface
│   ├── __init__.py
│   └── voice_server.py
├── config.py               # Configuration
├── main.py                 # Main entry point
├── load_mimic.py           # MIMIC data loader utility
├── requirements.txt        # Python dependencies
├── test_integration.py     # Integration tests
└── Dockerfile              # Docker build

### Frontend Directory (/frontend)
├── src/
│   ├── components/
│   │   ├── Appointments.css      # ✅ NEW
│   │   ├── Appointments.js       # ✅ ENHANCED
│   │   ├── Calls.js
│   │   ├── Dashboard.js
│   │   ├── Patients.css          # ✅ NEW  
│   │   ├── Patients.js           # ✅ ENHANCED
│   │   ├── PhoneInterface.css
│   │   └── PhoneInterface.js     # ✅ FIXED
│   ├── App.js
│   └── index.js
└── package.json

## Files Cleanup (can be safely deleted)

### Python Cache Files (__pycache__)
- All .pyc files (20 files total)
- These are automatically regenerated

### Action Required
**After stopping all services:**
1. Move medicalreceptionist.db to db/ folder:
   ```
   Move-Item backend/medicalreceptionist.db backend/db/
   ```

2. Delete all __pycache__ folders (optional, but recommended):
   ```
   Get-ChildItem -Path backend -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
   ```

## Project Structure Summary

Total Backend Files: 36 files
- Python modules: 17
- Configuration: 4
- Database: 1
- Documentation: 1
- Build: 2
- Cache (deletable): 20

Total Frontend Files: ~15-20 (Node modules excluded)
- Components: 8 (4 enhanced/new)
- Styles: 2 new CSS files
- Config: package.json

## Integration Points

1. **Frontend → Backend API**: http://localhost:8000/api
2. **Frontend → Voice Server**: Redirects to http://localhost:8003
3. **Voice Server → Backend Agent**: Direct import
4. **Agent → Medical Knowledge**: mimic/ modules
5. **Agent → Database**: db/ modules

## Recently Enhanced/Added Files

✅ urgent_care_knowledge.py - Comprehensive medical database
✅ urgent_care_handler.py - 8-step triage processor
✅ Patients.js + CSS - Table-based patient management
✅ Appointments.js + CSS - Table-based appointments
✅ PhoneInterface.js - Fixed redirect to voice server
✅ README.md - Complete documentation with medical sources

## Database Organization

Current: backend/medicalreceptionist.db
Should be: backend/db/medicalreceptionist.db

The .env already points to the correct location:
DATABASE_URL=sqlite:///./db/medicalreceptionist.db

After moving the file, .env will be properly aligned.
