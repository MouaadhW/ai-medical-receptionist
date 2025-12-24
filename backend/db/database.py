from sqlalchemy import createengine
from sqlalchemy.orm import sessionmaker
from loguru import logger
import config

Create engine
engine = createengine(
    config.config.DATABASEURL,
    connectargs={"checksamethread": False} if "sqlite" in config.config.DATABASEURL else {}
)

Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def getdb():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initdatabase():
    """Initialize database with tables"""
    from db.models import Base
    Base.metadata.createall(bind=engine)
    logger.info("Database initialized successfully")