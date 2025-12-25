from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger
import config

# Create engine
engine = create_engine(
    config.config.DATABASEURL,
    connect_args={"check_same_thread": False} if "sqlite" in config.config.DATABASEURL else {},
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def getdb():
    """Get database session (dependency)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initdatabase():
    """Initialize database with tables"""
    from db.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")