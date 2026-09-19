from app.core.db import get_pool

def list_all():
    sql = "SELECT idrolempleado, strdescripcion FROM tblroles ORDER BY idrolempleado DESC"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

def get_by_descripcion(descripcion: str):
    sql = "SELECT idrolempleado FROM tblroles WHERE lower(strdescripcion) = lower(%s)"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (descripcion,))
        return cur.fetchall()

def get_by_id(idrol: int):
    sql = "SELECT idrolempleado, strdescripcion FROM tblroles WHERE idrolempleado = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idrol,))
        return cur.fetchone()

def insert(descripcion: str) -> int:
    sql = "INSERT INTO tblroles (strdescripcion) VALUES (%s) RETURNING idrolempleado"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (descripcion,))
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id

def update(idrol: int, descripcion: str) -> None:
    sql = "UPDATE tblroles SET strdescripcion = %s WHERE idrolempleado = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (descripcion, idrol))
        conn.commit()

def delete(idrol: int) -> None:
    sql = "DELETE FROM tblroles WHERE idrolempleado = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idrol,))
        conn.commit()

def count_empleados_con_rol(idrol: int) -> int:
    sql = "SELECT count(*) FROM tblempleado WHERE idrolempleado = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idrol,))
        return cur.fetchone()[0]