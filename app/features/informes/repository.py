from app.core.db import get_pool

# --- VENTAS ---

def ventas_metricas(start_utc, end_utc):
    sql = """
        SELECT count(*), coalesce(sum(numvalortotal),0), coalesce(sum(numdescuento),0), coalesce(sum(numimpuesto),0)
        FROM tblfactura
        WHERE dtmfecha >= %s AND dtmfecha < %s AND idestado != 3
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (start_utc, end_utc))
        return cur.fetchone()

def ventas_por_dia(start_utc, end_utc, tz: str):
    sql = """
        SELECT (dtmfecha AT TIME ZONE 'UTC' AT TIME ZONE %s)::date AS dia,
               count(*), coalesce(sum(numvalortotal),0)
        FROM tblfactura
        WHERE dtmfecha >= %s AND dtmfecha < %s AND idestado != 3
        GROUP BY dia
        ORDER BY dia
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (tz, start_utc, end_utc))
        return cur.fetchall()

def ventas_top_productos(start_utc, end_utc):
    sql = """
        SELECT p.strnombre, sum(d.numcantidad) AS unidades, sum(d.numcantidad * d.numprecio) AS total
        FROM tbldetalle_factura d
        JOIN tblfactura f ON f.idfactura = d.idfactura
        JOIN tblproducto p ON p.idproducto = d.idproducto
        WHERE f.dtmfecha >= %s AND f.dtmfecha < %s AND f.idestado != 3
        GROUP BY p.strnombre
        ORDER BY total DESC
        LIMIT 5
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (start_utc, end_utc))
        return cur.fetchall()

def ventas_por_estado(start_utc, end_utc):
    sql = """
        SELECT e.strdescripcion, count(*), coalesce(sum(f.numvalortotal),0)
        FROM tblfactura f
        JOIN tblestado_factura e ON e.idestadofactura = f.idestado
        WHERE f.dtmfecha >= %s AND f.dtmfecha < %s
        GROUP BY e.strdescripcion
        ORDER BY e.strdescripcion
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (start_utc, end_utc))
        return cur.fetchall()

# --- INVENTARIO ---

def inventario_metricas(umbral: int):
    sql = """
        SELECT
            count(*),
            coalesce(sum(coalesce(numstock,0)),0),
            coalesce(sum(coalesce(numstock,0) * numpreciocompra),0),
            coalesce(sum(coalesce(numstock,0) * numprecioventa),0),
            count(*) FILTER (WHERE coalesce(numstock,0) < %s),
            count(*) FILTER (WHERE coalesce(numstock,0) = 0)
        FROM tblproducto
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (umbral,))
        return cur.fetchone()

def inventario_stock_bajo(umbral: int):
    sql = """
        SELECT strnombre, strcodigo, coalesce(numstock,0) AS stock
        FROM tblproducto
        WHERE coalesce(numstock,0) < %s
        ORDER BY stock ASC
        LIMIT 50
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (umbral,))
        return cur.fetchall()

def inventario_por_categoria():
    sql = """
        SELECT c.strdescripcion, count(p.idproducto), coalesce(sum(coalesce(p.numstock,0)),0),
               coalesce(sum(coalesce(p.numstock,0) * p.numprecioventa),0)
        FROM tblcategoria_prod c
        LEFT JOIN tblproducto p ON p.idcategoria = c.idcategoria
        GROUP BY c.strdescripcion
        ORDER BY c.strdescripcion
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

# --- FINANCIERO ---

def financiero_metricas(start_utc, end_utc):
    sql = """
        SELECT
            coalesce(sum(numvalortotal) FILTER (WHERE idestado != 3),0),
            coalesce(sum(numvalortotal) FILTER (WHERE idestado = 2),0),
            coalesce(sum(numvalortotal) FILTER (WHERE idestado = 1),0),
            coalesce(sum(numvalortotal) FILTER (WHERE idestado = 4),0),
            coalesce(sum(numvalortotal) FILTER (WHERE idestado = 3),0),
            coalesce(sum(numdescuento) FILTER (WHERE idestado != 3),0),
            coalesce(sum(numimpuesto) FILTER (WHERE idestado != 3),0)
        FROM tblfactura
        WHERE dtmfecha >= %s AND dtmfecha < %s
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (start_utc, end_utc))
        return cur.fetchone()

# --- EMPLEADOS ---

def ventas_por_empleado(start_utc, end_utc):
    sql = """
        SELECT e.strnombre, count(f.idfactura), coalesce(sum(f.numvalortotal),0)
        FROM tblfactura f
        JOIN tblempleado e ON e.idempleado = f.idempleado
        WHERE f.dtmfecha >= %s AND f.dtmfecha < %s AND f.idestado != 3
        GROUP BY e.strnombre
        ORDER BY 3 DESC
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (start_utc, end_utc))
        return cur.fetchall()

# --- CLIENTES ---

def compras_por_cliente(start_utc, end_utc):
    sql = """
        SELECT c.strnombre, c.numdocumento, count(f.idfactura), coalesce(sum(f.numvalortotal),0)
        FROM tblfactura f
        JOIN tblclientes c ON c.idcliente = f.idcliente
        WHERE f.dtmfecha >= %s AND f.dtmfecha < %s AND f.idestado != 3
        GROUP BY c.strnombre, c.numdocumento
        ORDER BY 4 DESC
        LIMIT 50
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (start_utc, end_utc))
        return cur.fetchall()