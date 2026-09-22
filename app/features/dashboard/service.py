from decimal import Decimal, ROUND_HALF_UP
from app.core.config import settings
from app.features.dashboard import repository

def _round2(v) -> Decimal:
    return Decimal(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def get_dashboard(permisos: list[str]):
    clientes = None
    if "clientes" in permisos:
        clientes = {"total": repository.count_clientes()}

    productos = None
    if "productos" in permisos:
        total, stock_bajo = repository.productos_stats(settings.STOCK_BAJO_UMBRAL)
        productos = {
            "total": total,
            "stock_bajo": stock_bajo,
            "umbral_stock_bajo": settings.STOCK_BAJO_UMBRAL,
        }

    empleados = None
    if "empleados" in permisos:
        empleados = {"total": repository.count_empleados_activos()}

    facturas = None
    if "facturas" in permisos or "informes" in permisos:
        total, pendientes, vencidas, ingresos_cobrados, por_cobrar = repository.facturas_stats()
        facturas = {
            "total": total,
            "pendientes": pendientes,
            "vencidas": vencidas,
            "ingresos_cobrados": _round2(ingresos_cobrados),
            "por_cobrar": _round2(por_cobrar),
        }

    return {
        "clientes": clientes,
        "productos": productos,
        "empleados": empleados,
        "facturas": facturas,
    }