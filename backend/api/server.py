from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from db.database import initdatabase
from loguru import logger
import config

app = FastAPI(
    title=config.config.APPNAME,
    version=config.config.VERSION,
    description="AI Medical Receptionist API"
)

CORS
app.addmiddleware(
    CORSMiddleware,
    alloworigins=[""],
    allowcredentials=True,
    allowmethods=[""],
    allowheaders=["*"],
)

Include routes
app.includerouter(router, prefix="/api")

@app.onevent("startup")
async def startupevent():
    """Initialize on startup"""
    logger.info(f"Starting {config.config.APPNAME} v{config.config.VERSION}")
    initdatabase()
    logger.info("Database initialized")

@app.get("/")
async def root():
    return {
        "name": config.config.APPNAME,
        "version": config.config.VERSION,
        "status": "healthy"
    }

@app.get("/health")
async def healthcheck():
    return {"status": "healthy", "version": config.config.VERSION}

if name == "main":
    import uvicorn
    uvicorn.run(
        app,
        host=config.config.APIHOST,
        port=config.config.APIPORT
    )