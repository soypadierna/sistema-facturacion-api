from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class CategoriaRefOut(CamelModel):
    id: int
    descripcion: str

class ProductoOut(CamelModel):
    id_producto: int
    nombre: str
    codigo: str
    precio_compra: Decimal
    precio_venta: Decimal
    categoria: CategoriaRefOut
    detalle: str | None
    foto_url: str | None
    stock: int
    fecha_modificacion: datetime | None
    modificado_por: str | None

class ProductoIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=70)
    codigo: str = Field(min_length=1, max_length=30)
    precio_compra: Decimal = Field(alias="precioCompra", gt=0, le=Decimal("999999999.99"))
    precio_venta: Decimal = Field(alias="precioVenta", gt=0, le=Decimal("999999999.99"))
    id_categoria: int = Field(alias="idCategoria")
    detalle: str | None = Field(default=None, max_length=50)
    stock: int = Field(default=0, ge=0)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("codigo", mode="before")
    @classmethod
    def _trim_codigo(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("precio_compra", "precio_venta")
    @classmethod
    def _check_decimals(cls, v: Decimal) -> Decimal:
        if v.as_tuple().exponent < -2:
            raise ValueError("Máximo 2 decimales")
        return v