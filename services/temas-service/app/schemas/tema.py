from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TemaBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=120)
    descripcion: str | None = Field(default=None, max_length=500)


class TemaCreate(TemaBase):
    materia_id: int = Field(gt=0)


class TemaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=120)
    descripcion: str | None = Field(default=None, max_length=500)
    materia_id: int | None = Field(default=None, gt=0)


class TemaResponse(TemaBase):
    id: str
    materia_id: int
    esta_activo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TemaPostsResponse(BaseModel):
    tema: TemaResponse
    posts: list[dict]
