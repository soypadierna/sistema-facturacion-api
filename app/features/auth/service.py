import logging
import time
from fastapi import HTTPException
from app.features.auth import repository
from app.core.security import hash_password, verify_hashed, verify_plain, create_token
from app.core.dates import is_retired
from app.core.permissions import get_permisos

logger = logging.getLogger("auth")

_FAILS: dict[str, list[float]] = {}
MAX_FAILS = 5
WINDOW_SECONDS = 15 * 60
GENERIC_ERROR = "Usuario o contraseña incorrectos"

def _rate_key(usuario: str, ip: str) -> str:
    return f"{usuario}:{ip}"

def _check_rate_limit(usuario: str, ip: str):
    key = _rate_key(usuario, ip)
    now = time.time()
    attempts = [t for t in _FAILS.get(key, []) if now - t < WINDOW_SECONDS]
    if attempts:
        _FAILS[key] = attempts
    else:
        _FAILS.pop(key, None)
    if len(attempts) >= MAX_FAILS:
        raise HTTPException(status_code=429, detail="Demasiados intentos, intente más tarde")

def _register_fail(usuario: str, ip: str):
    key = _rate_key(usuario, ip)
    _FAILS.setdefault(key, []).append(time.time())

def login(usuario: str, clave: str, ip: str) -> dict:
    _check_rate_limit(usuario, ip)

    rows = repository.get_by_usuario(usuario)
    if len(rows) == 0:
        _register_fail(usuario, ip)
        raise HTTPException(status_code=401, detail=GENERIC_ERROR)
    if len(rows) > 1:
        logger.warning("Multiples filas de seguridad para usuario=%s", usuario)
        _register_fail(usuario, ip)
        raise HTTPException(status_code=401, detail=GENERIC_ERROR)

    idseguridad, strclave, idempleado, strnombre, dtmretiro, idrol, roldesc, strpermisos = rows[0]

    if not strclave:
        _register_fail(usuario, ip)
        raise HTTPException(status_code=401, detail=GENERIC_ERROR)

    if is_retired(dtmretiro):
        _register_fail(usuario, ip)
        raise HTTPException(status_code=401, detail=GENERIC_ERROR)

    valid = False
    if strclave.startswith("s1$"):
        valid = verify_hashed(clave, usuario, strclave)
    else:
        if verify_plain(clave, strclave):
            valid = True
            repository.update_clave(idseguridad, hash_password(clave, usuario))

    if not valid:
        _register_fail(usuario, ip)
        raise HTTPException(status_code=401, detail=GENERIC_ERROR)

    _FAILS.pop(_rate_key(usuario, ip), None)

    token, expires_in = create_token(idempleado, idrol, usuario)
    permisos = get_permisos(idrol, strpermisos)
    return {
        "access_token": token,
        "expires_in": expires_in,
        "user": {
            "id_empleado": idempleado,
            "nombre": strnombre,
            "rol": {"id": idrol, "descripcion": roldesc},
            "permisos": permisos,
        },
    }

def get_me(idempleado: int) -> dict:
    rows = repository.get_by_idempleado(idempleado)
    if len(rows) == 0:
        raise HTTPException(status_code=401, detail=GENERIC_ERROR)

    idempleado, strnombre, dtmretiro, idrol, roldesc, strpermisos = rows[0]

    if is_retired(dtmretiro):
        raise HTTPException(status_code=401, detail=GENERIC_ERROR)

    permisos = get_permisos(idrol, strpermisos)
    return {
        "id_empleado": idempleado,
        "nombre": strnombre,
        "rol": {"id": idrol, "descripcion": roldesc},
        "permisos": permisos,
    }