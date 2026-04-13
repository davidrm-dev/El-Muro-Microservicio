from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TemaBase(BaseModel):
    """Schema base para Tema"""
    nombre: str = Field(..., min_length=3, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=1000)


class TemaCreate(TemaBase):
    """Schema para crear un Tema"""
    pass


class TemaResponse(TemaBase):
    """Schema para respuesta de Tema"""
    id: int
    materia_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MateriaBase(BaseModel):
    """Schema base para Materia"""
    nombre: str = Field(..., min_length=3, max_length=255, example="Programación I")
    descripcion: Optional[str] = Field(None, max_length=1000)
    semestre: int = Field(..., ge=1, le=10, example=1)
    carrera_id: int = Field(..., example=1)


class MateriaCreate(BaseModel):
    """Schema para crear Materia"""
    nombre: str = Field(..., min_length=3, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=1000)
    semestre: int = Field(..., ge=1, le=10)
    carrera_id: int


class MateriaUpdate(BaseModel):
    """Schema para actualizar Materia"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=1000)
    semestre: Optional[int] = Field(None, ge=1, le=10)


class MateriaResponse(MateriaBase):
    """Schema para respuesta de Materia"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MateriaDetailResponse(MateriaResponse):
    """Schema detallado de Materia con temas"""
    temas: List[TemaResponse] = []
