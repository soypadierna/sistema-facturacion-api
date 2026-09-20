from fastapi import APIRouter, Depends, Query, status
from app.core.deps import require_permission
from app.features.facturas import service
from app.features.facturas.schemas import (
    CatalogoOut, FacturaListItemOut, FacturaDetalleOut, FacturaCreate, EstadoUpdate,
)

router = APIRouter(prefix="/facturas", tags=["facturas"])

@router.get("/catalogo", response_model=CatalogoOut, response_model_by_alias=True)
def catalogo(_=Depends(require_permission("facturas"))):
    return service.get_catalogo()

@router.get("", response_model=list[FacturaListItemOut], response_model_by_alias=True)
def list_facturas(limit: int = Query(default=200, ge=1, le=500), _=Depends(require_permission("facturas"))):
    return service.list_facturas(limit)

@router.get("/{idfactura}", response_model=FacturaDetalleOut, response_model_by_alias=True)
def get_factura(idfactura: int, _=Depends(require_permission("facturas"))):
    return service.get_factura_detalle(idfactura)

@router.post("", response_model=FacturaDetalleOut, response_model_by_alias=True, status_code=status.HTTP_201_CREATED)
def create_factura(body: FacturaCreate, user=Depends(require_permission("facturas"))):
    return service.create_factura(body, user)

@router.patch("/{idfactura}/estado", response_model=FacturaDetalleOut, response_model_by_alias=True)
def update_estado(idfactura: int, body: EstadoUpdate, user=Depends(require_permission("facturas"))):
    return service.update_estado(idfactura, body.id_estado, user)