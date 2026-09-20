from datetime import timezone
from fastapi import HTTPException
import psycopg
from app.features.clientes import repository

def _to_out(row: tuple) -> dict:
    idcliente, nombre, documento, direccion, telefono, email, fecha, modificado_por = row
    return {
        "id_cliente": idcliente,
        "nombre": nombre,
        "documento": documento,
        "direccion": direccion,
        "telefono": telefono,
        "email": email,
        "fecha_modificacion": fecha.replace(tzinfo=timezone.utc) if fecha else None,
        "modificado_por": modificado_por,
    }

def list_clientes():
    return [_to_out(r) for r in repository.list_all()]

def _validate_documento(documento: int | None, current_id: int | None):
    if documento is None:
        return
    dup = repository.get_by_documento_excluding(documento, current_id)
    if dup:
        raise HTTPException(status_code=409, detail="Ya existe un cliente con ese documento")

def create_cliente(body, usuario: str):
    data = body.model_dump(by_alias=False)
    if data["email"]:
        data["email"] = data["email"].lower()
    _validate_documento(data["documento"], current_id=None)
    try:
        new_id = repository.insert(data, usuario)
    except psycopg.errors.IntegrityError:
        raise HTTPException(status_code=409, detail="No se pudo crear el cliente")
    return _to_out(repository.get_by_id(new_id))

def update_cliente(idcliente: int, body, usuario: str):
    if not repository.get_by_id(idcliente):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    data = body.model_dump(by_alias=False)
    if data["email"]:
        data["email"] = data["email"].lower()
    _validate_documento(data["documento"], current_id=idcliente)
    try:
        repository.update(idcliente, data, usuario)
    except psycopg.errors.IntegrityError:
        raise HTTPException(status_code=409, detail="No se pudo actualizar el cliente")
    return _to_out(repository.get_by_id(idcliente))

def delete_cliente(idcliente: int):
    if not repository.get_by_id(idcliente):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    count = repository.count_facturas(idcliente)
    if count > 0:
        raise HTTPException(status_code=409, detail=f"Cliente con {count} factura(s)")
    try:
        repository.delete(idcliente)
    except psycopg.errors.ForeignKeyViolation:
        raise HTTPException(status_code=409, detail="Cliente con facturas")