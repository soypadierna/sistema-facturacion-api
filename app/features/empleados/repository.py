from app.core.db import get_pool

_SELECT = """
    SELECT e.idempleado, e.strnombre, e.numdocumento, e.strdireccion, e.strtelefono,
           e.stremail, e.dtmingreso, e.dtmretiro, e.strdatosadicionales,
           r.idrolempleado, r.strdescripcion
    FROM tblempleado e
    LEFT JOIN tblroles r ON r.idrolempleado = e.idrolempleado
"""

def list_all(incluir_retirados: bool):
    sql = _SELECT
    if not incluir_retirados:
        sql += " WHERE (e.dtmretiro IS NULL OR e.dtmretiro > timezone('utc', now()))"
    sql += " ORDER BY e.idempleado DESC"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()
    
def get_by_id(idempleado: int):
    sql = _SELECT + " WHERE e.idempleado = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idempleado,))
        return cur.fetchone()

def get_by_documento(documento: int):
    sql = "SELECT idempleado FROM tblempleado WHERE numdocumento = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (documento,))
        return cur.fetchall()

def rol_exists(idrol: int) -> bool:
    sql = "SELECT 1 FROM tblroles WHERE idrolempleado = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idrol,))
        return cur.fetchone() is not None

def insert(data: dict, usuario: str) -> int:
    sql = """
        INSERT INTO tblempleado
            (strnombre, numdocumento, strdireccion, strtelefono, stremail,
             idrolempleado, dtmingreso, strdatosadicionales,
             dtmfechamodifica, strusuariomodifico)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, timezone('utc', now()), %s)
        RETURNING idempleado
    """
    params = (
        data["nombre"], data["documento"], data["direccion"], data["telefono"],
        data["email"], data["id_rol"], data["ingreso"], data["datos_adicionales"],
        usuario,
    )
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id

def update(idempleado: int, data: dict, usuario: str) -> None:
    sql = """
        UPDATE tblempleado
        SET strnombre = %s, numdocumento = %s, strdireccion = %s, strtelefono = %s,
            stremail = %s, idrolempleado = %s, dtmingreso = %s, strdatosadicionales = %s,
            dtmfechamodifica = timezone('utc', now()), strusuariomodifico = %s
        WHERE idempleado = %s
    """
    params = (
        data["nombre"], data["documento"], data["direccion"], data["telefono"],
        data["email"], data["id_rol"], data["ingreso"], data["datos_adicionales"],
        usuario, idempleado,
    )
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        conn.commit()

def retire(idempleado: int, usuario: str) -> int:
    sql = """
        UPDATE tblempleado
        SET dtmretiro = timezone('utc', now()), dtmfechamodifica = timezone('utc', now()),
            strusuariomodifico = %s
        WHERE idempleado = %s
          AND (dtmretiro IS NULL OR dtmretiro > timezone('utc', now()))
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (usuario, idempleado))
        conn.commit()
        return cur.rowcount
    
def reactivate(idempleado: int, usuario: str) -> None:
    sql = """
        UPDATE tblempleado
        SET dtmretiro = NULL, dtmfechamodifica = timezone('utc', now()),
            strusuariomodifico = %s
        WHERE idempleado = %s
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (usuario, idempleado))
        conn.commit()