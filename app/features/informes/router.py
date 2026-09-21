from datetime import date
from fastapi import APIRouter, Depends, Query
from app.core.deps import require_permission
from app.features.informes import service
from app.features.informes.schemas import TipoInformeOut, InformeOut

router = APIRouter(prefix="/informes", tags=["informes"])

@router.get("/tipos", response_model=list[TipoInformeOut], response_model_by_alias=True)
def list_tipos(user=Depends(require_permission("informes"))):
    return service.list_tipos(user)

@router.get("/{tipo}", response_model=InformeOut, response_model_by_alias=True)
def get_informe(
    tipo: str,
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
    user=Depends(require_permission("informes")),
):
    return service.get_informe(tipo, desde, hasta, user)