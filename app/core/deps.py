from dataclasses import dataclass
from fastapi import Header, HTTPException, Depends
import jwt
from app.core.security import decode_token
from app.core.permissions import get_permisos
from app.core.dates import is_retired
from app.features.auth import repository as auth_repository

@dataclass
class CurrentUser:
    id_empleado: int
    rol_id: int | None
    usuario: str
    permisos: list[str]

def get_current_user(authorization: str = Header(default="")) -> dict:
    headers = {"WWW-Authenticate": "Bearer"}
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autorizado", headers=headers)
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="No autorizado", headers=headers)
    if not str(payload.get("sub", "")).isdigit():
        raise HTTPException(status_code=401, detail="No autorizado", headers=headers)
    return payload

def require_permission(*perms: str):
    def dependency(payload: dict = Depends(get_current_user)) -> CurrentUser:
        headers = {"WWW-Authenticate": "Bearer"}
        idempleado = int(payload["sub"])
        usuario = payload.get("usr", "")
        rows = auth_repository.get_by_idempleado(idempleado)
        if len(rows) == 0:
            raise HTTPException(status_code=401, detail="No autorizado", headers=headers)
        _, _, dtmretiro, rol_id, _, strpermisos = rows[0]
        if is_retired(dtmretiro):
            raise HTTPException(status_code=401, detail="No autorizado", headers=headers)
        permisos = get_permisos(rol_id, strpermisos)
        if not any(p in permisos for p in perms):
            raise HTTPException(status_code=403, detail="Sin permiso")
        return CurrentUser(id_empleado=idempleado, rol_id=rol_id, usuario=usuario, permisos=permisos)
    return dependency