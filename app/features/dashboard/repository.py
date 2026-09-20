from app.core.db import get_pool

def count_clientes() -> int:
    sql = "SELECT count(*) FROM tblclientes"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchone()[0]

def productos_stats(umbral: int):
    sql = """
        SELECT count(*), count(*) FILTER (WHERE coalesce(numstock, 0) < %s)
        FROM tblproducto
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (umbral,))
        return cur.fetchone()

def count_empleados_activos() -> int:
    sql = """
        SELECT count(*) FROM tblempleado
        WHERE (dtmretiro IS NULL OR dtmretiro > timezone('utc', now()))
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchone()[0]

def facturas_stats():
    sql = """
        SELECT
            count(*) FILTER (WHERE idestado != 3),
            count(*) FILTER (WHERE idestado = 1),
            count(*) FILTER (WHERE idestado = 4),
            coalesce(sum(numvalortotal) FILTER (WHERE idestado = 2), 0),
            coalesce(sum(numvalortotal) FILTER (WHERE idestado IN (1, 4)), 0)
        FROM tblfactura
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchone()