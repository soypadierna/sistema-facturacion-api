from fastapi import HTTPException
from app.features.roles import repository

SYSTEM_ROLE_IDS = (1, 2, 3, 4)

def list_roles():
    rows = repository.list_all()
    return [{"id": r[0], "descripcion": r[1]} for r in rows]

def create_rol(descripcion: str):
    descripcion = descripcion.strip()
    if repository.get_by_descripcion(descripcion):
        raise HTTPException(status_code=409, detail="Ya existe un rol con esa descripción")
    new_id = repository.insert(descripcion)
    return {"id": new_id, "descripcion": descripcion}

def update_rol(idrol: int, descripcion: str):
    descripcion = descripcion.strip()
    if not repository.get_by_id(idrol):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    dup = repository.get_by_descripcion(descripcion)
    if dup and dup[0][0] != idrol:
        raise HTTPException(status_code=409, detail="Ya existe un rol con esa descripción")
    repository.update(idrol, descripcion)
    return {"id": idrol, "descripcion": descripcion}

def delete_rol(idrol: int):
    if not repository.get_by_id(idrol):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    if idrol in SYSTEM_ROLE_IDS:
        raise HTTPException(status_code=409, detail="Rol del sistema, no se puede eliminar")
    count = repository.count_empleados_con_rol(idrol)
    if count > 0:
        raise HTTPException(status_code=409, detail=f"Rol asignado a {count} empleado(s)")
    repository.delete(idrol)