from app.core.dates import is_retired
from app.core.permissions import ROLE_PERMISSIONS
from app.core.security import decode_token
from app.features.auth import repository as auth_repository
from dataclasses import dataclass
from datetime import datetime, timezone
from fastapi import Header, HTTPException, Depends
import jwt

@dataclass
class CurrentUser:
    id_empleado: int
    rol_id: int | None
    usuario: str

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
        _, _, dtmretiro, rol_id, _ = rows[0]
        if is_retired(dtmretiro):
            raise HTTPException(status_code=401, detail="No autorizado", headers=headers)
        allowed = ROLE_PERMISSIONS.get(rol_id, [])
        if not any(p in allowed for p in perms):
            raise HTTPException(status_code=403, detail="Sin permiso")
        return CurrentUser(id_empleado=idempleado, rol_id=rol_id, usuario=usuario)
    return dependency