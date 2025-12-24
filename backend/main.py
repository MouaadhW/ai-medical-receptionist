import sys
import os
sys.path.insert(0, os.path.dirname(file))

from api.server import app
from db.initdb import seeddatabase
from loguru import logger
import config

def initialize():
    """Initialize application"""
    logger.info("Initializing AI Medical Receptionist System...")
    
    # Seed database if needed
    try:
        seeddatabase()
    except Exception as e:
        logger.warning(f"Database already initialized: {e}")
    
    logger.info("Initialization complete")

if name == "main":
    import uvicorn
    
    initialize()
    
    logger.info(f"Starting {config.config.APPNAME} v{config.config.VERSION}")
    logger.info(f"API Server: http://{config.config.APIHOST}:{config.config.APIPORT}")
    logger.info(f"Voice Server: http://{config.config.APIHOST}:{config.config.VOICEPORT}")
    
    uvicorn.run(
        app,
        host=config.config.APIHOST,
        port=config.config.APIPORT,
        log_level="info"
    )