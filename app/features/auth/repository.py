from app.core.db import get_pool

def get_by_usuario(usuario: str):
    sql = """
        SELECT s.idseguridad, s.strclave, e.idempleado, e.strnombre, e.dtmretiro,
               r.idrolempleado, r.strdescripcion
        FROM tblseguridad s
        JOIN tblempleado e ON e.idempleado = s.idempleado
        LEFT JOIN tblroles r ON r.idrolempleado = e.idrolempleado
        WHERE s.strusuario = %s
    """
    with get_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (usuario,))
            return cur.fetchall()

def update_clave(idseguridad: int, nueva_clave: str) -> None:
    sql = """
        UPDATE tblseguridad
        SET strclave = %s, dtmfechamodifica = now(), strusuariomodifico = 'sistema'
        WHERE idseguridad = %s
    """
    with get_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (nueva_clave, idseguridad))
        conn.commit()

def get_by_idempleado(idempleado: int):
    sql = """
        SELECT e.idempleado, e.strnombre, e.dtmretiro,
               r.idrolempleado, r.strdescripcion
        FROM tblempleado e
        LEFT JOIN tblroles r ON r.idrolempleado = e.idrolempleado
        WHERE e.idempleado = %s
    """
    with get_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (idempleado,))
            return cur.fetchall()