from datetime import datetime, timezone
from fastapi import HTTPException
import psycopg
from app.features.empleados import repository

def _is_retired(dt) -> bool:
    if dt is None:
        return False
    return dt <= datetime.now(timezone.utc).replace(tzinfo=None)

def _to_out(row: tuple) -> dict:
    (idempleado, nombre, documento, direccion, telefono, email, ingreso, retiro,
     datos_adicionales, idrol, roldesc) = row
    return {
        "id_empleado": idempleado,
        "nombre": nombre,
        "documento": documento,
        "direccion": direccion,
        "telefono": telefono,
        "email": email,
        "ingreso": ingreso.date() if ingreso else None,
        "retiro": retiro.date() if retiro else None,
        "retirado": _is_retired(retiro),
        "datos_adicionales": datos_adicionales,
        "rol": {"id": idrol, "descripcion": roldesc} if idrol is not None else None,
    }

def list_empleados(incluir_retirados: bool):
    rows = repository.list_all(incluir_retirados)
    return [_to_out(r) for r in rows]

def _validate_common(data: dict, current_id: int | None):
    dup = repository.get_by_documento(data["documento"])
    dup_ids = [d[0] for d in dup]
    if any(i != current_id for i in dup_ids):
        raise HTTPException(status_code=409, detail="Ya existe un empleado con ese documento (puede estar retirado)")
    if data["id_rol"] is not None and not repository.rol_exists(data["id_rol"]):
        raise HTTPException(status_code=422, detail="Rol no existe")

def create_empleado(body, usuario: str):
    data = body.model_dump(by_alias=False)
    _validate_common(data, current_id=None)
    try:
        new_id = repository.insert(data, usuario)
    except psycopg.errors.IntegrityError:
        raise HTTPException(status_code=409, detail="No se pudo crear el empleado")
    row = repository.get_by_id(new_id)
    return _to_out(row)

def update_empleado(idempleado: int, body, current_user):
    row = repository.get_by_id(idempleado)
    if not row:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    data = body.model_dump(by_alias=False)
    _validate_common(data, current_id=idempleado)

    rol_actual = row[9]
    if idempleado == current_user.id_empleado and data["id_rol"] != rol_actual:
        raise HTTPException(status_code=409, detail="No puede cambiar su propio rol")

    try:
        repository.update(idempleado, data, current_user.usuario)
    except psycopg.errors.IntegrityError:
        raise HTTPException(status_code=409, detail="No se pudo actualizar el empleado")
    return _to_out(repository.get_by_id(idempleado))

def delete_empleado(idempleado: int, current_user):
    row = repository.get_by_id(idempleado)
    if not row:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    if idempleado == current_user.id_empleado:
        raise HTTPException(status_code=409, detail="No puede retirarse a sí mismo")
    rowcount = repository.retire(idempleado, current_user.usuario)
    if rowcount == 0:
        raise HTTPException(status_code=409, detail="El empleado ya está retirado")

def reactivar_empleado(idempleado: int, usuario: str):
    row = repository.get_by_id(idempleado)
    if not row:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    if not _is_retired(row[7]):
        raise HTTPException(status_code=409, detail="El empleado no está retirado")
    repository.reactivate(idempleado, usuario)
    return _to_out(repository.get_by_id(idempleado))

def reactivate(idempleado: int, usuario: str) -> None:
    sql = """
        UPDATE tblempleado
        SET dtmretiro = NULL, dtmfechamodifica = timezone('utc', now()),
            strusuariomodifico = %s
        WHERE idempleado = %s
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (usuario, idempleado))
        conn.commit()