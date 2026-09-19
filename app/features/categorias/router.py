from fastapi import APIRouter, Depends, status
from app.core.deps import require_permission
from app.features.categorias import service
from app.features.categorias.schemas import CategoriaOut, CategoriaCreate, CategoriaUpdate

router = APIRouter(prefix="/categorias", tags=["categorias"])

@router.get("", response_model=list[CategoriaOut], response_model_by_alias=True)
def list_categorias(_=Depends(require_permission("categorias", "productos"))):
    return service.list_categorias()

@router.post("", response_model=CategoriaOut, response_model_by_alias=True, status_code=status.HTTP_201_CREATED)
def create_categoria(body: CategoriaCreate, user=Depends(require_permission("categorias"))):
    return service.create_categoria(body.descripcion, user.usuario)

@router.put("/{idcategoria}", response_model=CategoriaOut, response_model_by_alias=True)
def update_categoria(idcategoria: int, body: CategoriaUpdate, user=Depends(require_permission("categorias"))):
    return service.update_categoria(idcategoria, body.descripcion, user.usuario)

@router.delete("/{idcategoria}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(idcategoria: int, _=Depends(require_permission("categorias"))):
    service.delete_categoria(idcategoria)