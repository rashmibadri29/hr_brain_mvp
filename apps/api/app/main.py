from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import health, mvp

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API foundation for the HR Operations Brain MVP.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(mvp.router, prefix="/api/v1", tags=["mvp"])

