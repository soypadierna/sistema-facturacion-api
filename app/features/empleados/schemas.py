from datetime import date
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class RolOut(CamelModel):
    id: int
    descripcion: str

class EmpleadoOut(CamelModel):
    id_empleado: int
    nombre: str
    documento: int
    direccion: str | None
    telefono: str | None
    email: str | None
    ingreso: date | None
    retiro: date | None
    retirado: bool
    datos_adicionales: str | None
    rol: RolOut | None

class EmpleadoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=50)
    documento: int = Field(ge=1, le=9223372036854775807)
    direccion: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    id_rol: int | None = Field(default=None, alias="idRol")
    ingreso: date | None = None
    datos_adicionales: str | None = Field(default=None, alias="datosAdicionales")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("direccion", "telefono", "datos_adicionales", mode="before")
    @classmethod
    def _empty_to_none(cls, v):
        return None if v == "" else v

class EmpleadoUpdate(EmpleadoCreate):
    pass