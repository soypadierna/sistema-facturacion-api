import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import psycopg
from app.core.config import settings
from app.features.auth.router import router as auth_router
from app.features.roles.router import router as roles_router
from app.features.empleados.router import router as empleados_router

logger = logging.getLogger("app")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(empleados_router)

@app.exception_handler(psycopg.OperationalError)
def operational_error_handler(request: Request, exc: psycopg.OperationalError):
    logger.exception("Error operacional de base de datos")
    return JSONResponse(status_code=503, content={"detail": "Servicio no disponible"})

@app.get("/health")
def health():
    return {"status": "ok"}