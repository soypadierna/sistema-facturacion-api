from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from app.core.config import settings
from app.core.permissions import ROLE_PERMISSIONS
from app.features.informes import repository

TIPOS_INFO = {
    "ventas": {"nombre": "Ventas", "requiereFechas": True},
    "inventario": {"nombre": "Inventario", "requiereFechas": False},
    "financiero": {"nombre": "Financiero", "requiereFechas": True},
    "empleados": {"nombre": "Empleados", "requiereFechas": True},
    "clientes": {"nombre": "Clientes", "requiereFechas": True},
}

# None => acceso especial (solo rol_id == 1), en vez de un permiso de ROLE_PERMISSIONS
REPORT_ACCESS = {
    "ventas": "facturas",
    "inventario": "productos",
    "empleados": "empleados",
    "clientes": "clientes",
    "financiero": None,
}

def _money(v) -> float:
    d = Decimal(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(d)

def _has_access(user, tipo: str) -> bool:
    permisos = ROLE_PERMISSIONS.get(user.rol_id, [])
    if "informes" not in permisos:
        return False
    requerido = REPORT_ACCESS[tipo]
    if requerido is None:
        return user.rol_id == 1
    return requerido in permisos

def list_tipos(user):
    result = []
    for tipo, info in TIPOS_INFO.items():
        if _has_access(user, tipo):
            result.append({"id": tipo, "nombre": info["nombre"], "requiere_fechas": info["requiereFechas"]})
    return result

def _rango_utc(desde: date, hasta: date):
    tz = ZoneInfo(settings.APP_TIMEZONE)
    start_local = datetime.combine(desde, time.min, tzinfo=tz)
    end_local = datetime.combine(hasta + timedelta(days=1), time.min, tzinfo=tz)
    start_utc = start_local.astimezone(timezone.utc).replace(tzinfo=None)
    end_utc = end_local.astimezone(timezone.utc).replace(tzinfo=None)
    return start_utc, end_utc

def _seccion_ventas(start_utc, end_utc):
    facturas, total, descuentos, impuestos = repository.ventas_metricas(start_utc, end_utc)
    ticket_prom = (Decimal(total) / facturas) if facturas > 0 else Decimal("0")

    metricas = {
        "kind": "metricas",
        "titulo": "Métricas generales",
        "items": [
            {"label": "Facturas", "value": float(facturas), "format": "entero"},
            {"label": "Total vendido", "value": _money(total), "format": "moneda"},
            {"label": "Descuentos", "value": _money(descuentos), "format": "moneda"},
            {"label": "Impuestos", "value": _money(impuestos), "format": "moneda"},
            {"label": "Ticket promedio", "value": _money(ticket_prom), "format": "moneda"},
        ],
    }

    por_dia = repository.ventas_por_dia(start_utc, end_utc, settings.APP_TIMEZONE)
    tabla_dia = {
        "kind": "tabla",
        "titulo": "Ventas por día",
        "columnas": [
            {"key": "fecha", "label": "Fecha", "format": "fecha"},
            {"key": "facturas", "label": "Facturas", "format": "entero"},
            {"key": "total", "label": "Total", "format": "moneda"},
        ],
        "filas": [
            {"fecha": r[0], "facturas": r[1], "total": _money(r[2])}
            for r in por_dia
        ],
    }

    top = repository.ventas_top_productos(start_utc, end_utc)
    tabla_top = {
        "kind": "tabla",
        "titulo": "Top 5 productos",
        "columnas": [
            {"key": "nombre", "label": "Producto", "format": "texto"},
            {"key": "unidades", "label": "Unidades", "format": "entero"},
            {"key": "total", "label": "Total", "format": "moneda"},
        ],
        "filas": [
            {"nombre": r[0], "unidades": r[1], "total": _money(r[2])}
            for r in top
        ],
    }

    por_estado = repository.ventas_por_estado(start_utc, end_utc)
    tabla_estado = {
        "kind": "tabla",
        "titulo": "Facturas por estado",
        "columnas": [
            {"key": "estado", "label": "Estado", "format": "texto"},
            {"key": "facturas", "label": "Facturas", "format": "entero"},
            {"key": "total", "label": "Total", "format": "moneda"},
        ],
        "filas": [
            {"estado": r[0], "facturas": r[1], "total": _money(r[2])}
            for r in por_estado
        ],
    }

    return [metricas, tabla_dia, tabla_top, tabla_estado]

def _seccion_inventario():
    umbral = settings.STOCK_BAJO_UMBRAL
    productos, unidades, valor_compra, valor_venta, stock_bajo, sin_stock = repository.inventario_metricas(umbral)

    metricas = {
        "kind": "metricas",
        "titulo": "Métricas de inventario",
        "items": [
            {"label": "Productos", "value": float(productos), "format": "entero"},
            {"label": "Unidades", "value": float(unidades), "format": "entero"},
            {"label": "Valor a precio de compra", "value": _money(valor_compra), "format": "moneda"},
            {"label": "Valor a precio de venta", "value": _money(valor_venta), "format": "moneda"},
            {"label": "Con stock bajo", "value": float(stock_bajo), "format": "entero"},
            {"label": "Sin stock", "value": float(sin_stock), "format": "entero"},
        ],
    }

    bajo = repository.inventario_stock_bajo(umbral)
    tabla_bajo = {
        "kind": "tabla",
        "titulo": "Stock bajo",
        "columnas": [
            {"key": "nombre", "label": "Producto", "format": "texto"},
            {"key": "codigo", "label": "Código", "format": "texto"},
            {"key": "stock", "label": "Stock", "format": "entero"},
        ],
        "filas": [
            {"nombre": r[0], "codigo": r[1], "stock": r[2]}
            for r in bajo
        ],
    }

    categorias = repository.inventario_por_categoria()
    tabla_cat = {
        "kind": "tabla",
        "titulo": "Por categoría",
        "columnas": [
            {"key": "categoria", "label": "Categoría", "format": "texto"},
            {"key": "productos", "label": "Productos", "format": "entero"},
            {"key": "unidades", "label": "Unidades", "format": "entero"},
            {"key": "valorVenta", "label": "Valor venta", "format": "moneda"},
        ],
        "filas": [
            {"categoria": r[0], "productos": r[1], "unidades": r[2], "valorVenta": _money(r[3])}
            for r in categorias
        ],
    }

    return [metricas, tabla_bajo, tabla_cat]

def _seccion_financiero(start_utc, end_utc):
    facturado, cobrado, pendiente, vencido, anulado, descuentos, impuestos = repository.financiero_metricas(start_utc, end_utc)
    metricas = {
        "kind": "metricas",
        "titulo": "Resumen financiero (por fecha de emisión)",
        "items": [
            {"label": "Facturado", "value": _money(facturado), "format": "moneda"},
            {"label": "Cobrado", "value": _money(cobrado), "format": "moneda"},
            {"label": "Pendiente", "value": _money(pendiente), "format": "moneda"},
            {"label": "Vencido", "value": _money(vencido), "format": "moneda"},
            {"label": "Anulado", "value": _money(anulado), "format": "moneda"},
            {"label": "Descuentos", "value": _money(descuentos), "format": "moneda"},
            {"label": "Impuestos", "value": _money(impuestos), "format": "moneda"},
        ],
    }
    return [metricas]

def _seccion_empleados(start_utc, end_utc):
    rows = repository.ventas_por_empleado(start_utc, end_utc)
    tabla = {
        "kind": "tabla",
        "titulo": "Ventas por empleado",
        "columnas": [
            {"key": "nombre", "label": "Empleado", "format": "texto"},
            {"key": "facturas", "label": "Facturas", "format": "entero"},
            {"key": "total", "label": "Total", "format": "moneda"},
        ],
        "filas": [
            {"nombre": r[0], "facturas": r[1], "total": _money(r[2])}
            for r in rows
        ],
    }
    return [tabla]

def _seccion_clientes(start_utc, end_utc):
    rows = repository.compras_por_cliente(start_utc, end_utc)
    tabla = {
        "kind": "tabla",
        "titulo": "Compras por cliente",
        "columnas": [
            {"key": "nombre", "label": "Cliente", "format": "texto"},
            {"key": "documento", "label": "Documento", "format": "texto"},
            {"key": "facturas", "label": "Facturas", "format": "entero"},
            {"key": "total", "label": "Total", "format": "moneda"},
        ],
        "filas": [
            {"nombre": r[0], "documento": r[1], "facturas": r[2], "total": _money(r[3])}
            for r in rows
        ],
    }
    return [tabla]

def get_informe(tipo: str, desde: date | None, hasta: date | None, user):
    if tipo not in TIPOS_INFO:
        raise HTTPException(status_code=404, detail="Tipo de informe no encontrado")

    if not _has_access(user, tipo):
        raise HTTPException(status_code=403, detail="Sin permiso")

    requiere_fechas = TIPOS_INFO[tipo]["requiereFechas"]

    if requiere_fechas:
        if desde is None or hasta is None:
            raise HTTPException(status_code=422, detail="Los parámetros desde y hasta son obligatorios")
        if hasta < desde:
            raise HTTPException(status_code=422, detail="hasta debe ser mayor o igual a desde")
        if (hasta - desde).days > 366:
            raise HTTPException(status_code=422, detail="El rango máximo permitido es de 366 días")
        start_utc, end_utc = _rango_utc(desde, hasta)
    else:
        desde = None
        hasta = None

    if tipo == "ventas":
        secciones = _seccion_ventas(start_utc, end_utc)
    elif tipo == "inventario":
        secciones = _seccion_inventario()
    elif tipo == "financiero":
        secciones = _seccion_financiero(start_utc, end_utc)
    elif tipo == "empleados":
        secciones = _seccion_empleados(start_utc, end_utc)
    elif tipo == "clientes":
        secciones = _seccion_clientes(start_utc, end_utc)
    else:
        raise HTTPException(status_code=404, detail="Tipo de informe no encontrado")

    return {
        "tipo": tipo,
        "titulo": f"Informe de {TIPOS_INFO[tipo]['nombre']}",
        "desde": desde,
        "hasta": hasta,
        "generado_en": datetime.now(timezone.utc),
        "secciones": secciones,
    }