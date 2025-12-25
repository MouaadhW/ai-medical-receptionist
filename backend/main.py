import sys
import os
from loguru import logger

# Ensure repo root is on path
sys.path.insert(0, os.path.dirname(__file__))

from api.server import app
from db.init_db import seeddatabase
import config


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