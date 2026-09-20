import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import psycopg
from app.core.config import settings
from app.features.auth.router import router as auth_router
from app.features.roles.router import router as roles_router
from app.features.empleados.router import router as empleados_router
from app.features.usuarios.router import router as usuarios_router
from app.features.categorias.router import router as categorias_router
from app.features.productos.router import router as productos_router
from app.features.clientes.router import router as clientes_router

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
app.include_router(usuarios_router)
app.include_router(categorias_router)
app.include_router(productos_router)
app.include_router(clientes_router)

def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])

@app.exception_handler(RequestValidationError)
def validation_error_handler(request: Request, exc: RequestValidationError):
    campos = []
    for err in exc.errors():
        loc = err.get("loc", [])
        if loc:
            campos.append(_to_camel(str(loc[-1])))
    detalle = "Datos inválidos: " + ", ".join(dict.fromkeys(campos))
    return JSONResponse(status_code=422, content={"detail": detalle})

@app.exception_handler(psycopg.OperationalError)
def operational_error_handler(request: Request, exc: psycopg.OperationalError):
    logger.exception("Error operacional de base de datos")
    return JSONResponse(status_code=503, content={"detail": "Servicio no disponible"})

@app.get("/health")
def health():
    return {"status": "ok"}