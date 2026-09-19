from fastapi import APIRouter, Depends, Query, status
from app.core.deps import require_permission
from app.features.empleados import service
from app.features.empleados.schemas import EmpleadoOut, EmpleadoCreate, EmpleadoUpdate

router = APIRouter(prefix="/empleados", tags=["empleados"])

@router.get("", response_model=list[EmpleadoOut], response_model_by_alias=True)
def list_empleados(incluirRetirados: bool = Query(default=False), user=Depends(require_permission("empleados"))):
    return service.list_empleados(incluirRetirados)

@router.post("", response_model=EmpleadoOut, response_model_by_alias=True, status_code=status.HTTP_201_CREATED)
def create_empleado(body: EmpleadoCreate, user=Depends(require_permission("empleados"))):
    return service.create_empleado(body, user.usuario)

@router.put("/{idempleado}", response_model=EmpleadoOut, response_model_by_alias=True)
def update_empleado(idempleado: int, body: EmpleadoUpdate, user=Depends(require_permission("empleados"))):
    return service.update_empleado(idempleado, body, user)

@router.delete("/{idempleado}", status_code=status.HTTP_204_NO_CONTENT)
def delete_empleado(idempleado: int, user=Depends(require_permission("empleados"))):
    service.delete_empleado(idempleado, user)
    
@router.patch("/{idempleado}/reactivar", response_model=EmpleadoOut, response_model_by_alias=True)
def reactivar_empleado(idempleado: int, user=Depends(require_permission("empleados"))):
    return service.reactivar_empleado(idempleado, user.usuario)