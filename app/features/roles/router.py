from fastapi import APIRouter, Depends, status
from app.core.deps import require_permission
from app.features.roles import service
from app.features.roles.schemas import RolOut, RolCreate, RolUpdate

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("/modulos", response_model=list[str])
def get_modulos(_=Depends(require_permission("roles"))):
    return service.get_modulos()

@router.get("", response_model=list[RolOut], response_model_by_alias=True)
def list_roles(_=Depends(require_permission("roles", "empleados"))):
    return service.list_roles()

@router.post("", response_model=RolOut, response_model_by_alias=True, status_code=status.HTTP_201_CREATED)
def create_rol(body: RolCreate, _=Depends(require_permission("roles"))):
    return service.create_rol(body.descripcion, body.permisos)

@router.put("/{idrol}", response_model=RolOut, response_model_by_alias=True)
def update_rol(idrol: int, body: RolUpdate, _=Depends(require_permission("roles"))):
    return service.update_rol(idrol, body.descripcion, body.permisos)

@router.delete("/{idrol}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rol(idrol: int, _=Depends(require_permission("roles"))):
    service.delete_rol(idrol)