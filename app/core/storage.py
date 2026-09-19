from urllib.parse import quote
import httpx
from app.core.config import settings

_client = httpx.Client(timeout=10)

def upload_object(nombre: str, content: bytes) -> None:
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_STORAGE_BUCKET}/{quote(nombre, safe='')}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_KEY,
        "Content-Type": "image/webp",
        "cache-control": "max-age=31536000",
    }
    resp = _client.post(url, headers=headers, content=content)
    resp.raise_for_status()

def delete_object(nombre: str) -> None:
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_STORAGE_BUCKET}/{quote(nombre, safe='')}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_KEY,
    }
    resp = _client.delete(url, headers=headers)
    resp.raise_for_status()

def build_foto_url(strfoto: str | None) -> str | None:
    if not strfoto:
        return None
    if strfoto.startswith(("http://", "https://")):
        return strfoto
    return f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_STORAGE_BUCKET}/{quote(strfoto, safe='')}"