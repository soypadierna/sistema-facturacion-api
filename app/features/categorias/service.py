from datetime import timezone
from fastapi import HTTPException
import psycopg
from app.features.categorias import repository

def _to_out(row: tuple) -> dict:
    idcategoria, descripcion, fecha, modificado_por = row
    return {
        "id": idcategoria,
        "descripcion": descripcion,
        "fecha_modificacion": fecha.replace(tzinfo=timezone.utc) if fecha else None,
        "modificado_por": modificado_por,
    }

def list_categorias():
    return [_to_out(r) for r in repository.list_all()]

def create_categoria(descripcion: str, usuario: str):
    descripcion = descripcion.strip()
    if repository.get_by_descripcion_excluding(descripcion, None):
        raise HTTPException(status_code=409, detail="Ya existe una categoría con esa descripción")
    try:
        new_id = repository.insert(descripcion, usuario)
    except psycopg.errors.IntegrityError:
        raise HTTPException(status_code=409, detail="No se pudo crear la categoría")
    return _to_out(repository.get_by_id(new_id))

def update_categoria(idcategoria: int, descripcion: str, usuario: str):
    descripcion = descripcion.strip()
    if not repository.get_by_id(idcategoria):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    if repository.get_by_descripcion_excluding(descripcion, idcategoria):
        raise HTTPException(status_code=409, detail="Ya existe una categoría con esa descripción")
    try:
        repository.update(idcategoria, descripcion, usuario)
    except psycopg.errors.IntegrityError:
        raise HTTPException(status_code=409, detail="No se pudo actualizar la categoría")
    return _to_out(repository.get_by_id(idcategoria))

def delete_categoria(idcategoria: int):
    if not repository.get_by_id(idcategoria):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    count = repository.count_productos(idcategoria)
    if count > 0:
        raise HTTPException(status_code=409, detail=f"Categoría con {count} producto(s)")
    repository.delete(idcategoria)