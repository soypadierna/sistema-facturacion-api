import logging
import httpx
from app.core.config import settings

logger = logging.getLogger("storage")

def upload_object(nombre: str, content: bytes) -> None:
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_STORAGE_BUCKET}/{nombre}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_KEY,
        "Content-Type": "image/webp",
    }
    resp = httpx.post(url, headers=headers, content=content, timeout=30)
    resp.raise_for_status()

def delete_object(nombre: str) -> None:
    if not nombre or nombre.startswith("http"):
        return
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_STORAGE_BUCKET}/{nombre}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_KEY,
    }
    try:
        httpx.delete(url, headers=headers, timeout=30)
    except Exception:
        logger.warning("No se pudo borrar el objeto %s del storage", nombre)

def build_foto_url(strfoto: str | None) -> str | None:
    if not strfoto:
        return None
    if strfoto.startswith("http"):
        return strfoto
    return f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_STORAGE_BUCKET}/{strfoto}"