import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.routes import router
from app.core.config import settings

# Configure loguru logger
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)

app = FastAPI(
    title="AI Kubernetes Troubleshooting Agent",
    version="0.1.0",
    description="On-demand Kubernetes investigation and troubleshooting system."
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


# Also mount health endpoint directly at root level as specified in prompt (GET /health)
@app.get("/health")
def root_health():
    return {"status": "healthy", "service": "ai-kubernetes-agent"}


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME} backend service...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.PROJECT_NAME} backend service...")
