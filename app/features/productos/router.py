from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.core.deps import require_permission
from app.features.productos import service
from app.features.productos.schemas import ProductoOut, ProductoIn

router = APIRouter(prefix="/productos", tags=["productos"])

MAX_PHOTO_BYTES = 3 * 1024 * 1024

@router.get("", response_model=list[ProductoOut], response_model_by_alias=True)
def list_productos(_=Depends(require_permission("productos"))):
    return service.list_productos()

@router.post("", response_model=ProductoOut, response_model_by_alias=True, status_code=status.HTTP_201_CREATED)
def create_producto(body: ProductoIn, user=Depends(require_permission("productos"))):
    return service.create_producto(body, user.usuario)

@router.put("/{idproducto}", response_model=ProductoOut, response_model_by_alias=True)
def update_producto(idproducto: int, body: ProductoIn, user=Depends(require_permission("productos"))):
    return service.update_producto(idproducto, body, user.usuario)

@router.delete("/{idproducto}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(idproducto: int, _=Depends(require_permission("productos"))):
    service.delete_producto(idproducto)

@router.post("/{idproducto}/foto", response_model=ProductoOut, response_model_by_alias=True)
def upload_foto(idproducto: int, file: UploadFile = File(...), user=Depends(require_permission("productos"))):
    raw = file.file.read(MAX_PHOTO_BYTES + 1)
    if len(raw) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=413, detail="La imagen supera el tamaño máximo de 3 MB")
    return service.upload_foto(idproducto, raw, user.usuario)

@router.delete("/{idproducto}/foto", status_code=status.HTTP_204_NO_CONTENT)
def delete_foto(idproducto: int, user=Depends(require_permission("productos"))):
    service.delete_foto(idproducto, user.usuario)