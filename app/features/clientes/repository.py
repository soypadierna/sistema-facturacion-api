from app.core.db import get_pool

def list_all():
    sql = """
        SELECT idcliente, strnombre, numdocumento, strdireccion, strtelefono, stremail,
               dtmfechamodifica, strusuariomodifica
        FROM tblclientes ORDER BY idcliente DESC
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

def get_by_id(idcliente: int):
    sql = """
        SELECT idcliente, strnombre, numdocumento, strdireccion, strtelefono, stremail,
               dtmfechamodifica, strusuariomodifica
        FROM tblclientes WHERE idcliente = %s
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idcliente,))
        return cur.fetchone()

def get_by_documento_excluding(documento: int, idcliente: int | None):
    sql = "SELECT idcliente FROM tblclientes WHERE numdocumento = %s"
    params: tuple = (documento,)
    if idcliente is not None:
        sql += " AND idcliente != %s"
        params = (documento, idcliente)
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

def insert(data: dict, usuario: str) -> int:
    sql = """
        INSERT INTO tblclientes
            (strnombre, numdocumento, strdireccion, strtelefono, stremail,
             dtmfechamodifica, strusuariomodifica)
        VALUES (%s, %s, %s, %s, %s, timezone('utc', now()), %s)
        RETURNING idcliente
    """
    params = (data["nombre"], data["documento"], data["direccion"], data["telefono"], data["email"], usuario)
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id

def update(idcliente: int, data: dict, usuario: str) -> None:
    sql = """
        UPDATE tblclientes
        SET strnombre = %s, numdocumento = %s, strdireccion = %s, strtelefono = %s, stremail = %s,
            dtmfechamodifica = timezone('utc', now()), strusuariomodifica = %s
        WHERE idcliente = %s
    """
    params = (data["nombre"], data["documento"], data["direccion"], data["telefono"], data["email"], usuario, idcliente)
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        conn.commit()

def delete(idcliente: int) -> None:
    sql = "DELETE FROM tblclientes WHERE idcliente = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idcliente,))
        conn.commit()

def count_facturas(idcliente: int) -> int:
    sql = "SELECT count(*) FROM tblfactura WHERE idcliente = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idcliente,))
        return cur.fetchone()[0]