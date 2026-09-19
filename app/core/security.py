import base64
import hashlib
import hmac
import time
import jwt
from app.core.config import settings

def hash_password(clave: str, usuario: str) -> str:
    salt = f"{settings.PASSWORD_PEPPER}:{usuario}".encode()
    dk = hashlib.scrypt(clave.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return "s1$" + base64.b64encode(dk).decode()

def verify_hashed(clave: str, usuario: str, stored_hash: str) -> bool:
    computed = hash_password(clave, usuario)
    return hmac.compare_digest(computed.encode("utf-8"), stored_hash.encode("utf-8"))

def verify_plain(clave: str, stored_plain: str) -> bool:
    return hmac.compare_digest(clave.encode("utf-8"), stored_plain.encode("utf-8"))

def create_token(idempleado: int, idrolempleado, usuario: str) -> tuple[str, int]:
    expires_in = settings.JWT_EXPIRE_MINUTES * 60
    payload = {
        "sub": str(idempleado),
        "rol": idrolempleado,
        "usr": usuario,
        "exp": int(time.time()) + expires_in,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token, expires_in

def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=["HS256"],
        options={"require": ["exp", "sub", "usr"]},
    )