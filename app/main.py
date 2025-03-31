from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager
import os
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.router import api_router
from app.core.config import settings
from app.core.logging_config import logger

# Создаем middleware для добавления специальных заголовков безопасности
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Разрешаем date picker в iframe
        response.headers["Cross-Origin-Embedder-Policy"] = "credentialless"
        # Разрешаем интеграцию через iframe
        response.headers["X-Frame-Options"] = "ALLOWALL"
        # Устанавливаем политику доступа к документу
        response.headers["Cross-Origin-Opener-Policy"] = "unsafe-none"
        # Разрешаем выполнение скриптов с других источников
        response.headers["Content-Security-Policy"] = "frame-ancestors *"
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code executed when the application starts
    logger.info("Starting API service optimization of the energy market")
    yield
    # Code executed when the application stops
    logger.info("Stopping API service")

# Create an instance of FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for optimizing charge/discharge cycles of energy storage facilities",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Test-Data"],  # Allow access to the X-Test-Data header
)

# Connect API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files for UI
static_dir = Path(__file__).parent.parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.on_event("startup")
async def startup_event():
    """Event when the application starts"""
    logger.info("Starting API service optimization of the energy market")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Root route, returns HTML page"""
    return FileResponse("static/index.html")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
