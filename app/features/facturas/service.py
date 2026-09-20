from decimal import Decimal, ROUND_HALF_UP
from datetime import timezone
from fastapi import HTTPException
import psycopg
from app.core.db import get_pool
from app.core.config import settings
from app.core.storage import build_foto_url
from app.features.facturas import repository

TRANSICIONES: dict[int, set[int]] = {
    1: {2, 3, 4},
    2: {3},
    4: {2, 3},
    3: set(),
}

def _round2(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def _estado_ref(idestado: int, descripcion: str) -> dict:
    return {"id": idestado, "descripcion": descripcion}

def get_catalogo():
    estados = [_estado_ref(e[0], e[1]) for e in repository.get_estados()]
    productos = [
        {
            "id_producto": p[0],
            "nombre": p[1],
            "codigo": p[2],
            "precio_venta": p[3],
            "stock": p[4],
            "foto_url": build_foto_url(p[5]),
        }
        for p in repository.get_catalogo_productos()
    ]
    return {
        "impuesto_porcentaje": settings.IVA_PORCENTAJE,
        "estados": estados,
        "productos": productos,
    }

def _to_list_item(row: tuple) -> dict:
    (idfactura, fecha, idcliente, cliente_nombre, idempleado, empleado_nombre,
     idestado, estado_desc, total) = row
    return {
        "id_factura": idfactura,
        "fecha": fecha.replace(tzinfo=timezone.utc) if fecha else None,
        "cliente": {"id": idcliente, "nombre": cliente_nombre},
        "empleado": {"id": idempleado, "nombre": empleado_nombre},
        "estado": _estado_ref(idestado, estado_desc),
        "total": total,
        "estados_permitidos": sorted(TRANSICIONES.get(idestado, set())),
    }

def list_facturas(limit: int):
    return [_to_list_item(r) for r in repository.list_facturas(limit)]

def get_factura_detalle(idfactura: int):
    row = repository.get_factura_full(idfactura)
    if not row:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    (idfactura_, fecha, idcliente, cliente_nombre, idempleado, empleado_nombre,
     idestado, estado_desc, total, descuento, impuesto) = row
    subtotal = total - impuesto + descuento  # base + impuesto - impuesto + descuento? recompute properly below

    # recompute subtotal precisely from detalle sum to avoid drift
    detalle_rows = repository.get_detalles(idfactura)
    detalles = []
    subtotal_calc = Decimal("0")
    for d in detalle_rows:
        iddetalle, idproducto, nombre, codigo, cantidad, precio = d
        line_subtotal = _round2(Decimal(precio) * cantidad)
        subtotal_calc += line_subtotal
        detalles.append({
            "id_detalle": iddetalle,
            "id_producto": idproducto,
            "nombre": nombre,
            "codigo": codigo,
            "cantidad": cantidad,
            "precio": precio,
            "subtotal": line_subtotal,
        })

    return {
        "id_factura": idfactura_,
        "fecha": fecha.replace(tzinfo=timezone.utc) if fecha else None,
        "cliente": {"id": idcliente, "nombre": cliente_nombre},
        "empleado": {"id": idempleado, "nombre": empleado_nombre},
        "estado": _estado_ref(idestado, estado_desc),
        "total": total,
        "estados_permitidos": sorted(TRANSICIONES.get(idestado, set())),
        "subtotal": subtotal_calc,
        "descuento": descuento,
        "impuesto": impuesto,
        "detalles": detalles,
    }

def create_factura(body, current_user):
    if not repository.cliente_exists(body.id_cliente):
        raise HTTPException(status_code=422, detail="Cliente no existe")

    combinadas: dict[int, int] = {}
    for linea in body.detalles:
        combinadas[linea.id_producto] = combinadas.get(linea.id_producto, 0) + linea.cantidad

    ids = sorted(combinadas.keys())

    try:
        with get_pool().connection() as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    rows = repository.lock_productos(cur, ids)
                    productos_por_id = {r[0]: r for r in rows}

                    faltantes = [i for i in ids if i not in productos_por_id]
                    if faltantes:
                        raise HTTPException(status_code=422, detail="Producto no existe")

                    subtotal = Decimal("0")
                    lineas_calculadas = []
                    for idproducto in ids:
                        cantidad = combinadas[idproducto]
                        _, nombre, precio_venta, stock = productos_por_id[idproducto]
                        stock = stock or 0
                        if stock < cantidad:
                            raise HTTPException(
                                status_code=409,
                                detail=f"Stock insuficiente para {nombre} (disponible {stock})",
                            )
                        precio = Decimal(precio_venta)
                        line_subtotal = _round2(precio * cantidad)
                        subtotal += line_subtotal
                        lineas_calculadas.append((idproducto, cantidad, precio))

                    descuento = _round2(subtotal * body.descuento_porcentaje / Decimal("100"))
                    base = subtotal - descuento
                    impuesto = _round2(base * settings.IVA_PORCENTAJE / Decimal("100"))
                    total = base + impuesto

                    idfactura = repository.insert_factura(
                        cur, body.id_cliente, current_user.id_empleado,
                        descuento, impuesto, total, body.id_estado, current_user.usuario,
                    )

                    for idproducto, cantidad, precio in lineas_calculadas:
                        repository.insert_detalle(cur, idfactura, idproducto, cantidad, precio)
                        repository.decrement_stock(cur, idproducto, cantidad, current_user.usuario)

    except HTTPException:
        raise
    except psycopg.errors.IntegrityError:
        raise HTTPException(status_code=409, detail="No se pudo crear la factura")

    return get_factura_detalle(idfactura)

def update_estado(idfactura: int, nuevo_estado: int, current_user):
    try:
        with get_pool().connection() as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    row = repository.lock_factura(cur, idfactura)
                    if not row:
                        raise HTTPException(status_code=404, detail="Factura no encontrada")
                    _, estado_actual = row

                    permitidos = TRANSICIONES.get(estado_actual, set())
                    if nuevo_estado not in permitidos:
                        raise HTTPException(
                            status_code=409,
                            detail=f"No se puede pasar de {estado_actual} a {nuevo_estado}",
                        )

                    if nuevo_estado == 3:
                        detalle_rows = repository.get_detalles_for_lock(cur, idfactura)
                        ids = [d[0] for d in detalle_rows]
                        if ids:
                            repository.lock_productos(cur, sorted(set(ids)))
                        for idproducto, cantidad in detalle_rows:
                            repository.increment_stock(cur, idproducto, cantidad, current_user.usuario)

                    repository.update_estado(cur, idfactura, nuevo_estado, current_user.usuario)

    except HTTPException:
        raise
    except psycopg.errors.IntegrityError:
        raise HTTPException(status_code=409, detail="No se pudo actualizar el estado")

    return get_factura_detalle(idfactura)