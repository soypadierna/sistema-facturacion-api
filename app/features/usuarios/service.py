import logging
from datetime import datetime, timezone
from fastapi import HTTPException
import psycopg
from app.features.usuarios import repository
from app.core.security import hash_password

logger = logging.getLogger("usuarios")

def _is_retired(dt) -> bool:
    if dt is None:
        return False
    return dt <= datetime.now(timezone.utc).replace(tzinfo=None)

def list_usuarios():
    rows = repository.list_activos()
    result = []
    seen = set()
    for idempleado, nombre, usuario, idseguridad in rows:
        if idempleado in seen:
            continue
        seen.add(idempleado)
        result.append({"id_empleado": idempleado, "nombre": nombre, "usuario": usuario})
    return result

def set_credenciales(idempleado: int, usuario: str, clave: str, current_user):
    emp = repository.get_empleado(idempleado)
    if not emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    _, dtmretiro = emp
    if _is_retired(dtmretiro):
        raise HTTPException(status_code=409, detail="El empleado está retirado")

    dup = repository.get_by_usuario_excluding(usuario, idempleado)
    if dup:
        raise HTTPException(status_code=409, detail="Ese usuario ya está en uso")

    rows = repository.get_seguridad_by_empleado(idempleado)
    clave_hash = hash_password(clave, usuario)

    if len(rows) == 0:
        try:
            repository.insert(idempleado, usuario, clave_hash, current_user.usuario)
        except psycopg.errors.IntegrityError:
            raise HTTPException(status_code=409, detail="No se pudo crear la credencial")
        return {"id_empleado": idempleado, "usuario": usuario, "creado": True}

    if len(rows) > 1:
        logger.warning("Credenciales duplicadas para idempleado=%s", idempleado)
        raise HTTPException(status_code=409, detail="Credenciales duplicadas, revisar en base de datos")

    idseguridad = rows[0][0]
    try:
        repository.update(idseguridad, usuario, clave_hash, current_user.usuario)
    except psycopg.errors.IntegrityError:
        raise HTTPException(status_code=409, detail="No se pudo actualizar la credencial")
    return {"id_empleado": idempleado, "usuario": usuario, "creado": False}