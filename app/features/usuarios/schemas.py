from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class UsuarioOut(CamelModel):
    id_empleado: int
    nombre: str
    usuario: str | None

class CredencialesIn(BaseModel):
    usuario: str = Field(min_length=3, max_length=50)
    clave: str = Field(min_length=6, max_length=50)

    @field_validator("usuario")
    @classmethod
    def _validate_usuario(cls, v: str) -> str:
        import re
        v = v.strip()
        if not re.fullmatch(r"[A-Za-z0-9._-]{3,50}", v):
            raise ValueError("Usuario inválido: solo letras, números, puntos, guiones y guion bajo (3-50 caracteres)")
        return v

class CredencialesOut(CamelModel):
    id_empleado: int
    usuario: str
    creado: bool