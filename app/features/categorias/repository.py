from app.core.db import get_pool

def list_all():
    sql = """
        SELECT idcategoria, strdescripcion, dtmfechamodifica, strusuariomodifico
        FROM tblcategoria_prod ORDER BY idcategoria DESC
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

def get_by_id(idcategoria: int):
    sql = """
        SELECT idcategoria, strdescripcion, dtmfechamodifica, strusuariomodifico
        FROM tblcategoria_prod WHERE idcategoria = %s
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idcategoria,))
        return cur.fetchone()

def get_by_descripcion_excluding(descripcion: str, idcategoria: int | None):
    sql = "SELECT idcategoria FROM tblcategoria_prod WHERE lower(strdescripcion) = lower(%s)"
    params: tuple = (descripcion,)
    if idcategoria is not None:
        sql += " AND idcategoria != %s"
        params = (descripcion, idcategoria)
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

def insert(descripcion: str, usuario: str) -> int:
    sql = """
        INSERT INTO tblcategoria_prod (strdescripcion, dtmfechamodifica, strusuariomodifico)
        VALUES (%s, timezone('utc', now()), %s) RETURNING idcategoria
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (descripcion, usuario))
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id

def update(idcategoria: int, descripcion: str, usuario: str) -> None:
    sql = """
        UPDATE tblcategoria_prod
        SET strdescripcion = %s, dtmfechamodifica = timezone('utc', now()), strusuariomodifico = %s
        WHERE idcategoria = %s
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (descripcion, usuario, idcategoria))
        conn.commit()

def delete(idcategoria: int) -> None:
    sql = "DELETE FROM tblcategoria_prod WHERE idcategoria = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idcategoria,))
        conn.commit()

def count_productos(idcategoria: int) -> int:
    sql = "SELECT count(*) FROM tblproducto WHERE idcategoria = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idcategoria,))
        return cur.fetchone()[0]