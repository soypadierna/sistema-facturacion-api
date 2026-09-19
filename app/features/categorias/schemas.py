from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class CategoriaOut(CamelModel):
    id: int
    descripcion: str
    fecha_modificacion: datetime | None
    modificado_por: str | None

class CategoriaCreate(BaseModel):
    descripcion: str = Field(min_length=1, max_length=60)

class CategoriaUpdate(BaseModel):
    descripcion: str = Field(min_length=1, max_length=60)