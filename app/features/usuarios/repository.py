from app.core.db import get_pool

def list_activos():
    sql = """
        SELECT e.idempleado, e.strnombre, s.strusuario, s.idseguridad
        FROM tblempleado e
        LEFT JOIN tblseguridad s ON s.idempleado = e.idempleado
        WHERE (e.dtmretiro IS NULL OR e.dtmretiro > timezone('utc', now()))
        ORDER BY e.strnombre, s.idseguridad
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

def get_empleado(idempleado: int):
    sql = "SELECT idempleado, dtmretiro FROM tblempleado WHERE idempleado = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idempleado,))
        return cur.fetchone()

def get_seguridad_by_empleado(idempleado: int):
    sql = "SELECT idseguridad, strusuario FROM tblseguridad WHERE idempleado = %s ORDER BY idseguridad"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idempleado,))
        return cur.fetchall()

def get_by_usuario_excluding(usuario: str, idempleado: int):
    sql = """
        SELECT s.idseguridad FROM tblseguridad s
        WHERE lower(s.strusuario) = lower(%s) AND s.idempleado != %s
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (usuario, idempleado))
        return cur.fetchall()

def insert(idempleado: int, usuario: str, clave_hash: str, usuario_modifico: str) -> None:
    sql = """
        INSERT INTO tblseguridad (idempleado, strusuario, strclave, dtmfechamodifica, strusuariomodifico)
        VALUES (%s, %s, %s, timezone('utc', now()), %s)
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idempleado, usuario, clave_hash, usuario_modifico))
        conn.commit()

def update(idseguridad: int, usuario: str, clave_hash: str, usuario_modifico: str) -> None:
    sql = """
        UPDATE tblseguridad
        SET strusuario = %s, strclave = %s, dtmfechamodifica = timezone('utc', now()),
            strusuariomodifico = %s
        WHERE idseguridad = %s
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (usuario, clave_hash, usuario_modifico, idseguridad))
        conn.commit()