import json
from fastapi import HTTPException
from app.features.roles import repository
from app.core.permissions import MODULOS_DISPONIBLES, get_permisos

SYSTEM_ROLE_IDS = (1, 2, 3, 4)

def _to_out(row: tuple) -> dict:
    idrol, descripcion, strpermisos = row
    return {"id": idrol, "descripcion": descripcion, "permisos": get_permisos(idrol, strpermisos)}

def list_roles():
    rows = repository.list_all()
    return [_to_out(r) for r in rows]

def get_modulos():
    return MODULOS_DISPONIBLES

def _validate_permisos(permisos: list[str] | None):
    if permisos is None:
        return
    for p in permisos:
        if p not in MODULOS_DISPONIBLES:
            raise HTTPException(status_code=422, detail=f"Módulo no válido: {p}")

def create_rol(descripcion: str, permisos: list[str] | None):
    descripcion = descripcion.strip()
    if repository.get_by_descripcion(descripcion):
        raise HTTPException(status_code=409, detail="Ya existe un rol con esa descripción")
    _validate_permisos(permisos)
    strpermisos = json.dumps(permisos) if permisos is not None else '["dashboard"]'
    new_id = repository.insert(descripcion, strpermisos)
    return _to_out(repository.get_by_id(new_id))

def update_rol(idrol: int, descripcion: str, permisos: list[str] | None):
    descripcion = descripcion.strip()
    if not repository.get_by_id(idrol):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    dup = repository.get_by_descripcion(descripcion)
    if dup and dup[0][0] != idrol:
        raise HTTPException(status_code=409, detail="Ya existe un rol con esa descripción")
    _validate_permisos(permisos)
    strpermisos = json.dumps(permisos) if permisos is not None else None
    repository.update_descripcion_permisos(idrol, descripcion, strpermisos)
    return _to_out(repository.get_by_id(idrol))

def delete_rol(idrol: int):
    if not repository.get_by_id(idrol):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    if idrol in SYSTEM_ROLE_IDS:
        raise HTTPException(status_code=409, detail="Rol del sistema, no se puede eliminar")
    count = repository.count_empleados_con_rol(idrol)
    if count > 0:
        raise HTTPException(status_code=409, detail=f"Rol asignado a {count} empleado(s)")
    repository.delete(idrol)