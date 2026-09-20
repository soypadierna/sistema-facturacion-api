from app.core.db import get_pool

def get_estados():
    sql = "SELECT idestadofactura, strdescripcion FROM tblestado_factura ORDER BY idestadofactura"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

def get_catalogo_productos():
    sql = """
        SELECT idproducto, strnombre, strcodigo, numprecioventa, numstock, strfoto
        FROM tblproducto WHERE numstock > 0 ORDER BY strnombre
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

_LIST_SELECT = """
    SELECT f.idfactura, f.dtmfecha, f.idcliente, cl.strnombre,
           f.idempleado, emp.strnombre, f.idestado, est.strdescripcion, f.numvalortotal
    FROM tblfactura f
    JOIN tblclientes cl ON cl.idcliente = f.idcliente
    JOIN tblempleado emp ON emp.idempleado = f.idempleado
    JOIN tblestado_factura est ON est.idestadofactura = f.idestado
"""

def list_facturas(limit: int):
    sql = _LIST_SELECT + " ORDER BY f.idfactura DESC LIMIT %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (limit,))
        return cur.fetchall()

def get_factura(idfactura: int):
    sql = _LIST_SELECT + " WHERE f.idfactura = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idfactura,))
        return cur.fetchone()

def get_factura_full(idfactura: int):
    sql = """
        SELECT f.idfactura, f.dtmfecha, f.idcliente, cl.strnombre,
               f.idempleado, emp.strnombre, f.idestado, est.strdescripcion,
               f.numvalortotal, f.numdescuento, f.numimpuesto
        FROM tblfactura f
        JOIN tblclientes cl ON cl.idcliente = f.idcliente
        JOIN tblempleado emp ON emp.idempleado = f.idempleado
        JOIN tblestado_factura est ON est.idestadofactura = f.idestado
        WHERE f.idfactura = %s
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idfactura,))
        return cur.fetchone()

def get_detalles(idfactura: int):
    sql = """
        SELECT d.iddetalle, d.idproducto, p.strnombre, p.strcodigo, d.numcantidad, d.numprecio
        FROM tbldetalle_factura d
        JOIN tblproducto p ON p.idproducto = d.idproducto
        WHERE d.idfactura = %s
        ORDER BY d.iddetalle
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idfactura,))
        return cur.fetchall()

def cliente_exists(idcliente: int) -> bool:
    sql = "SELECT 1 FROM tblclientes WHERE idcliente = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idcliente,))
        return cur.fetchone() is not None

def lock_productos(cur, ids: list[int]):
    sql = """
        SELECT idproducto, strnombre, numprecioventa, numstock
        FROM tblproducto WHERE idproducto = ANY(%s)
        ORDER BY idproducto
        FOR UPDATE
    """
    cur.execute(sql, (ids,))
    return cur.fetchall()

def insert_factura(cur, idcliente, idempleado, descuento, impuesto, total, idestado, usuario) -> int:
    sql = """
        INSERT INTO tblfactura
            (dtmfecha, idcliente, idempleado, numdescuento, numimpuesto, numvalortotal,
             idestado, dtmfechamodifica, strusuariomodifica)
        VALUES (timezone('utc', now()), %s, %s, %s, %s, %s, %s, timezone('utc', now()), %s)
        RETURNING idfactura
    """
    cur.execute(sql, (idcliente, idempleado, descuento, impuesto, total, idestado, usuario))
    return cur.fetchone()[0]

def insert_detalle(cur, idfactura, idproducto, cantidad, precio):
    sql = """
        INSERT INTO tbldetalle_factura (idfactura, numcantidad, idproducto, numprecio)
        VALUES (%s, %s, %s, %s)
    """
    cur.execute(sql, (idfactura, cantidad, idproducto, precio))

def decrement_stock(cur, idproducto, cantidad, usuario):
    sql = """
        UPDATE tblproducto
        SET numstock = numstock - %s, dtmfechamodifica = timezone('utc', now()), strusuariomodifica = %s
        WHERE idproducto = %s
    """
    cur.execute(sql, (cantidad, usuario, idproducto))

def increment_stock(cur, idproducto, cantidad, usuario):
    sql = """
        UPDATE tblproducto
        SET numstock = coalesce(numstock, 0) + %s, dtmfechamodifica = timezone('utc', now()), strusuariomodifica = %s
        WHERE idproducto = %s
    """
    cur.execute(sql, (cantidad, usuario, idproducto))

def lock_factura(cur, idfactura: int):
    sql = "SELECT idfactura, idestado FROM tblfactura WHERE idfactura = %s FOR UPDATE"
    cur.execute(sql, (idfactura,))
    return cur.fetchone()

def update_estado(cur, idfactura: int, idestado: int, usuario: str):
    sql = """
        UPDATE tblfactura
        SET idestado = %s, dtmfechamodifica = timezone('utc', now()), strusuariomodifica = %s
        WHERE idfactura = %s
    """
    cur.execute(sql, (idestado, usuario, idfactura))

def get_detalles_for_lock(cur, idfactura: int):
    sql = """
        SELECT idproducto, numcantidad FROM tbldetalle_factura
        WHERE idfactura = %s ORDER BY idproducto
    """
    cur.execute(sql, (idfactura,))
    return cur.fetchall()