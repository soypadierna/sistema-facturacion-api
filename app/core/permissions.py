import json

MODULOS_DISPONIBLES = [
    "dashboard", "clientes", "productos", "categorias", "facturas",
    "informes", "empleados", "roles", "crear-admin",
]

def get_permisos(rol_id: int | None, strpermisos: str | None) -> list[str]:
    if rol_id == 1:
        return list(MODULOS_DISPONIBLES)
    if not strpermisos:
        return ["dashboard"]
    try:
        raw = json.loads(strpermisos)
    except (ValueError, TypeError):
        return ["dashboard"]
    if not isinstance(raw, list):
        return ["dashboard"]
    return [p for p in raw if p in MODULOS_DISPONIBLES]