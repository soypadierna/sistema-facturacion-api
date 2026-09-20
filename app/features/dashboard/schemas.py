from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class ClientesBlock(CamelModel):
    total: int

class ProductosBlock(CamelModel):
    total: int
    stock_bajo: int
    umbral_stock_bajo: int

class EmpleadosBlock(CamelModel):
    total: int

class FacturasBlock(CamelModel):
    total: int
    pendientes: int
    vencidas: int
    ingresos_cobrados: Decimal
    por_cobrar: Decimal

class DashboardOut(CamelModel):
    clientes: ClientesBlock | None
    productos: ProductosBlock | None
    empleados: EmpleadosBlock | None
    facturas: FacturasBlock | None