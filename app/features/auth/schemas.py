from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class LoginRequest(BaseModel):
    usuario: str
    clave: str

class RolOut(CamelModel):
    id: int | None
    descripcion: str | None

class UserOut(CamelModel):
    id_empleado: int
    nombre: str
    rol: RolOut
    permisos: list[str]

class LoginResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut