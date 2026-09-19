from app.core.db import get_pool

_SELECT = """
    SELECT p.idproducto, p.strnombre, p.strcodigo, p.numpreciocompra, p.numprecioventa,
           p.strdetalle, p.strfoto, p.numstock, p.dtmfechamodifica, p.strusuariomodifica,
           c.idcategoria, c.strdescripcion
    FROM tblproducto p
    JOIN tblcategoria_prod c ON c.idcategoria = p.idcategoria
"""

def list_all():
    sql = _SELECT + " ORDER BY p.idproducto DESC"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

def get_by_id(idproducto: int):
    sql = _SELECT + " WHERE p.idproducto = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idproducto,))
        return cur.fetchone()

def get_by_codigo_excluding(codigo: str, idproducto: int | None):
    sql = "SELECT idproducto FROM tblproducto WHERE lower(strcodigo) = lower(%s)"
    params: tuple = (codigo,)
    if idproducto is not None:
        sql += " AND idproducto != %s"
        params = (codigo, idproducto)
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

def categoria_exists(idcategoria: int) -> bool:
    sql = "SELECT 1 FROM tblcategoria_prod WHERE idcategoria = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idcategoria,))
        return cur.fetchone() is not None

def insert(data: dict, usuario: str) -> int:
    sql = """
        INSERT INTO tblproducto
            (strnombre, strcodigo, numpreciocompra, numprecioventa, idcategoria,
             strdetalle, numstock, dtmfechamodifica, strusuariomodifica)
        VALUES (%s, %s, %s, %s, %s, %s, %s, timezone('utc', now()), %s)
        RETURNING idproducto
    """
    params = (
        data["nombre"], data["codigo"], data["precio_compra"], data["precio_venta"],
        data["id_categoria"], data["detalle"], data["stock"], usuario,
    )
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id

def update(idproducto: int, data: dict, usuario: str) -> None:
    sql = """
        UPDATE tblproducto
        SET strnombre = %s, strcodigo = %s, numpreciocompra = %s, numprecioventa = %s,
            idcategoria = %s, strdetalle = %s, numstock = %s,
            dtmfechamodifica = timezone('utc', now()), strusuariomodifica = %s
        WHERE idproducto = %s
    """
    params = (
        data["nombre"], data["codigo"], data["precio_compra"], data["precio_venta"],
        data["id_categoria"], data["detalle"], data["stock"], usuario, idproducto,
    )
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        conn.commit()

def delete(idproducto: int) -> None:
    sql = "DELETE FROM tblproducto WHERE idproducto = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idproducto,))
        conn.commit()

def count_facturas_usando(idproducto: int) -> int:
    sql = "SELECT count(*) FROM tbldetalle_factura WHERE idproducto = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idproducto,))
        return cur.fetchone()[0]

def get_strfoto(idproducto: int):
    sql = "SELECT strfoto FROM tblproducto WHERE idproducto = %s"
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (idproducto,))
        row = cur.fetchone()
        return row[0] if row else None

def update_foto(idproducto: int, strfoto: str | None, usuario: str) -> None:
    sql = """
        UPDATE tblproducto
        SET strfoto = %s, dtmfechamodifica = timezone('utc', now()), strusuariomodifica = %s
        WHERE idproducto = %s
    """
    with get_pool().connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (strfoto, usuario, idproducto))
        conn.commit()