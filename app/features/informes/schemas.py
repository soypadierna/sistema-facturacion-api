from datetime import date, datetime
from typing import Literal, Union, Annotated
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class TipoInformeOut(CamelModel):
    id: str
    nombre: str
    requiere_fechas: bool

class MetricaItem(CamelModel):
    label: str
    value: float
    format: Literal["moneda", "entero"]

class SeccionMetricas(CamelModel):
    kind: Literal["metricas"] = "metricas"
    titulo: str
    items: list[MetricaItem]

class ColumnaOut(CamelModel):
    key: str
    label: str
    format: Literal["moneda", "entero", "texto", "fecha"]

class SeccionTabla(CamelModel):
    kind: Literal["tabla"] = "tabla"
    titulo: str
    columnas: list[ColumnaOut]
    filas: list[dict]

Seccion = Annotated[Union[SeccionMetricas, SeccionTabla], Field(discriminator="kind")]

class InformeOut(CamelModel):
    tipo: str
    titulo: str
    desde: date | None
    hasta: date | None
    generado_en: datetime
    secciones: list[Seccion]