from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class ClienteOut(CamelModel):
    id_cliente: int
    nombre: str
    documento: int | None
    direccion: str | None
    telefono: str | None
    email: str | None
    fecha_modificacion: datetime | None
    modificado_por: str | None

class ClienteIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=55)
    documento: int | None = Field(default=None, ge=1, le=9223372036854775807)
    direccion: str | None = Field(default=None, max_length=70)
    telefono: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("nombre", mode="before")
    @classmethod
    def _trim_nombre(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("direccion", "telefono", mode="before")
    @classmethod
    def _trim_or_none(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v

    @field_validator("email", mode="before")
    @classmethod
    def _email_or_none(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v