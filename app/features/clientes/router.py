from fastapi import APIRouter, Depends, status
from app.core.deps import require_permission
from app.features.clientes import service
from app.features.clientes.schemas import ClienteOut, ClienteIn

router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.get("", response_model=list[ClienteOut], response_model_by_alias=True)
def list_clientes(_=Depends(require_permission("clientes", "facturas"))):
    return service.list_clientes()

@router.post("", response_model=ClienteOut, response_model_by_alias=True, status_code=status.HTTP_201_CREATED)
def create_cliente(body: ClienteIn, user=Depends(require_permission("clientes"))):
    return service.create_cliente(body, user.usuario)

@router.put("/{idcliente}", response_model=ClienteOut, response_model_by_alias=True)
def update_cliente(idcliente: int, body: ClienteIn, user=Depends(require_permission("clientes"))):
    return service.update_cliente(idcliente, body, user.usuario)

@router.delete("/{idcliente}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cliente(idcliente: int, _=Depends(require_permission("clientes"))):
    service.delete_cliente(idcliente)