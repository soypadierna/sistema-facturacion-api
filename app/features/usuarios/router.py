from fastapi import APIRouter, Depends, Response, status
from app.core.deps import require_permission
from app.features.usuarios import service
from app.features.usuarios.schemas import UsuarioOut, CredencialesIn, CredencialesOut

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.get("", response_model=list[UsuarioOut], response_model_by_alias=True)
def list_usuarios(_=Depends(require_permission("crear-admin"))):
    return service.list_usuarios()

@router.put("/{idempleado}/credenciales", response_model=CredencialesOut, response_model_by_alias=True)
def set_credenciales(idempleado: int, body: CredencialesIn, response: Response, user=Depends(require_permission("crear-admin"))):
    result = service.set_credenciales(idempleado, body.usuario, body.clave, user)
    response.status_code = status.HTTP_201_CREATED if result["creado"] else status.HTTP_200_OK
    return result