from fastapi import FastAPI
from app.core.config import settings
from app.utils.logger import setup_logger
from app.api.routes import auth

logger = setup_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Ticket Management System API"}
