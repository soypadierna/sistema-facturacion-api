import logging
from decimal import Decimal, ROUND_HALF_UP
from datetime import timezone
from uuid import uuid4
from io import BytesIO
from fastapi import HTTPException
import psycopg
from PIL import Image, ImageOps
from app.features.productos import repository
from app.core.storage import upload_object, delete_object, build_foto_url

logger = logging.getLogger("productos")

Image.MAX_IMAGE_PIXELS = 25_000_000

MAX_PHOTO_BYTES = 3 * 1024 * 1024
MAX_SIDE = 800

def _q2(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def _to_out(row: tuple) -> dict:
    (idproducto, nombre, codigo, precio_compra, precio_venta, detalle, strfoto,
     stock, fecha, modificado_por, idcategoria, cat_desc) = row
    return {
        "id_producto": idproducto,
        "nombre": nombre,
        "codigo": codigo,
        "precio_compra": precio_compra,
        "precio_venta": precio_venta,
        "categoria": {"id": idcategoria, "descripcion": cat_desc},
        "detalle": detalle,
        "foto_url": build_foto_url(strfoto),
        "stock": stock,
        "fecha_modificacion": fecha.replace(tzinfo=timezone.utc) if fecha else None,
        "modificado_por": modificado_por,
    }

def list_productos():
    return [_to_out(r) for r in repository.list_all()]

def _validate_common(data: dict, current_id: int | None):
    if not repository.categoria_exists(data["id_categoria"]):
        raise HTTPException(status_code=422, detail="Categoría no existe")
    dup = repository.get_by_codigo_excluding(data["codigo"], current_id)
    if dup:
        raise HTTPException(status_code=409, detail="Ya existe un producto con ese código")

def create_producto(body, usuario: str):
    data = body.model_dump(by_alias=False)
    data["precio_compra"] = _q2(data["precio_compra"])
    data["precio_venta"] = _q2(data["precio_venta"])
    _validate_common(data, current_id=None)
    try:
        new_id = repository.insert(data, usuario)
    except psycopg.errors.IntegrityError:
        raise HTTPException(status_code=409, detail="No se pudo crear el producto")
    return _to_out(repository.get_by_id(new_id))

def update_producto(idproducto: int, body, usuario: str):
    if not repository.get_by_id(idproducto):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    data = body.model_dump(by_alias=False)
    data["precio_compra"] = _q2(data["precio_compra"])
    data["precio_venta"] = _q2(data["precio_venta"])
    _validate_common(data, current_id=idproducto)
    try:
        repository.update(idproducto, data, usuario)
    except psycopg.errors.IntegrityError:
        raise HTTPException(status_code=409, detail="No se pudo actualizar el producto")
    return _to_out(repository.get_by_id(idproducto))

def _safe_delete(nombre: str | None) -> None:
    if not nombre or nombre.startswith("http"):
        return
    try:
        delete_object(nombre)
    except Exception:
        logger.warning("No se pudo borrar el objeto %s del storage", nombre)

def delete_producto(idproducto: int):
    row = repository.get_by_id(idproducto)
    if not row:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    count = repository.count_facturas_usando(idproducto)
    if count > 0:
        raise HTTPException(status_code=409, detail=f"Producto usado en {count} factura(s)")
    strfoto = row[6]
    try:
        repository.delete(idproducto)
    except psycopg.errors.ForeignKeyViolation:
        raise HTTPException(status_code=409, detail="Producto usado en facturas")
    _safe_delete(strfoto)

def _process_image(raw: bytes) -> bytes:
    try:
        img = Image.open(BytesIO(raw))
        img.verify()
        img = Image.open(BytesIO(raw))

        if img.format not in ("JPEG", "PNG", "WEBP"):
            raise ValueError("Formato no soportado")

        img = ImageOps.exif_transpose(img)

        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGBA")
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            img = img.convert("RGB")

        img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)

        out = BytesIO()
        img.save(out, format="WEBP", quality=80)
        return out.getvalue()
    except Exception:
        raise HTTPException(status_code=415, detail="El archivo no es una imagen válida")

def upload_foto(idproducto: int, raw: bytes, usuario: str):
    row = repository.get_by_id(idproducto)
    if not row:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    processed = _process_image(raw)
    nombre = f"{uuid4()}.webp"

    try:
        upload_object(nombre, processed)
    except Exception:
        logger.exception("Fallo al subir imagen a Storage para idproducto=%s", idproducto)
        raise HTTPException(status_code=502, detail="No se pudo subir la imagen")

    old_foto = row[6]
    try:
        repository.update_foto(idproducto, nombre, usuario)
    except psycopg.errors.IntegrityError:
        _safe_delete(nombre)
        raise HTTPException(status_code=409, detail="No se pudo actualizar el producto")
    except Exception:
        _safe_delete(nombre)
        raise

    _safe_delete(old_foto)

    return _to_out(repository.get_by_id(idproducto))

def delete_foto(idproducto: int, usuario: str):
    row = repository.get_by_id(idproducto)
    if not row:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    strfoto = row[6]
    repository.update_foto(idproducto, None, usuario)
    _safe_delete(strfoto)