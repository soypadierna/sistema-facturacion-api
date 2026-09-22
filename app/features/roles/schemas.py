from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class RolOut(CamelModel):
    id: int
    descripcion: str
    permisos: list[str]

class RolCreate(BaseModel):
    descripcion: str = Field(min_length=1, max_length=50)
    permisos: list[str] | None = None

class RolUpdate(BaseModel):
    descripcion: str = Field(min_length=1, max_length=50)
    permisos: list[str] | None = None