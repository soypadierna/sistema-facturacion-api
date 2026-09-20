from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class ClienteRefOut(CamelModel):
    id: int
    nombre: str

class EmpleadoRefOut(CamelModel):
    id: int
    nombre: str

class EstadoRefOut(CamelModel):
    id: int
    descripcion: str

class ProductoCatalogoOut(CamelModel):
    id_producto: int
    nombre: str
    codigo: str
    precio_venta: Decimal
    stock: int
    foto_url: str | None

class CatalogoOut(CamelModel):
    impuesto_porcentaje: Decimal
    estados: list[EstadoRefOut]
    productos: list[ProductoCatalogoOut]

class FacturaListItemOut(CamelModel):
    id_factura: int
    fecha: datetime
    cliente: ClienteRefOut
    empleado: EmpleadoRefOut
    estado: EstadoRefOut
    total: Decimal
    estados_permitidos: list[int]

class DetalleOut(CamelModel):
    id_detalle: int
    id_producto: int
    nombre: str
    codigo: str
    cantidad: int
    precio: Decimal
    subtotal: Decimal

class FacturaDetalleOut(FacturaListItemOut):
    subtotal: Decimal
    descuento: Decimal
    impuesto: Decimal
    detalles: list[DetalleOut]

class DetalleLineaIn(BaseModel):
    id_producto: int = Field(alias="idProducto")
    cantidad: int = Field(ge=1, le=100000)

    model_config = ConfigDict(populate_by_name=True)

class FacturaCreate(BaseModel):
    id_cliente: int = Field(alias="idCliente")
    id_estado: Literal[1, 2] = Field(default=1, alias="idEstado")
    descuento_porcentaje: Decimal = Field(default=Decimal("0"), alias="descuentoPorcentaje", ge=0, le=100)
    detalles: list[DetalleLineaIn] = Field(min_length=1, max_length=100)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("descuento_porcentaje")
    @classmethod
    def _check_decimals(cls, v: Decimal) -> Decimal:
        if v.as_tuple().exponent < -2:
            raise ValueError("Máximo 2 decimales")
        return v

class EstadoUpdate(BaseModel):
    id_estado: int = Field(alias="idEstado")

    model_config = ConfigDict(populate_by_name=True)