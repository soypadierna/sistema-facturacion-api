from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class LoginRequest(BaseModel):
    usuario: str = Field(min_length=1, max_length=50)
    clave: str = Field(min_length=1, max_length=50)

class RolOut(CamelModel):
    id: int | None
    descripcion: str | None

class UserOut(CamelModel):
    id_empleado: int
    nombre: str
    rol: RolOut

class LoginResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut