import sys
import os
from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure repo root is on path
sys.path.insert(0, os.path.dirname(__file__))

from api import routes
from api.billing_routes import router as billing_router
from api.medical_history_routes import router as medical_history_router
from db.init_db import seeddatabase
import config

app = FastAPI(title=config.config.APPNAME, version=config.config.VERSION)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include existing routes
app.include_router(routes.router, prefix="/api")

# Include new patient-centric module routes
app.include_router(billing_router)
app.include_router(medical_history_router)


def initialize():
    """Initialize application"""
    logger.info("Initializing AI Medical Receptionist System...")

    # Seed database if needed
    try:
        seeddatabase()
    except Exception as e:
        logger.warning(f"Database already initialized or seeding failed: {e}")

    logger.info("Initialization complete")


if __name__ == "__main__":
    import uvicorn

    initialize()

    logger.info(f"Starting {config.config.APPNAME} v{config.config.VERSION}")
    logger.info(f"API Server: http://{config.config.APIHOST}:{config.config.APIPORT}")
    logger.info(f"Voice Server: http://{config.config.APIHOST}:{config.config.VOICEPORT}")

    uvicorn.run(
        app,
        host=config.config.APIHOST,
        port=config.config.APIPORT,
        log_level="info",
    )