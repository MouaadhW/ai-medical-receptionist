from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from db.database import initdatabase
from loguru import logger
import config


app = FastAPI(
    title=config.config.APPNAME,
    version=config.config.VERSION,
    description="AI Medical Receptionist API",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info(f"Starting {config.config.APPNAME} v{config.config.VERSION}")
    initdatabase()
    logger.info("Database initialized")


@app.get("/")
async def root():
    return {
        "name": config.config.APPNAME,
        "version": config.config.VERSION,
        "status": "healthy",
    }


@app.get("/health")
async def healthcheck():
    return {"status": "healthy", "version": config.config.VERSION}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.config.APIHOST, port=config.config.APIPORT)