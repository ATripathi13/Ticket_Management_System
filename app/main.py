from fastapi import FastAPI
from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Ticket Management System API"}
