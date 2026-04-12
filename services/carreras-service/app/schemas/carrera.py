from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CarreraBase(BaseModel):
    """Schema base para Carrera"""
    nombre: str = Field(..., min_length=3, max_length=255, example="Ingeniería de Sistemas")
    descripcion: Optional[str] = Field(None, max_length=1000, example="Descripción de la carrera")


class CarreraCreate(CarreraBase):
    """Schema para crear una Carrera"""
    pass


class CarreraUpdate(BaseModel):
    """Schema para actualizar una Carrera"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=1000)


class CarreraResponse(CarreraBase):
    """Schema para respuesta de Carrera"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CarreraDetailResponse(CarreraResponse):
    """Schema detallado de Carrera con materias"""
    materias: List["MateriaResponse"] = []


class MateriaBase(BaseModel):
    """Schema base para Materia"""
    nombre: str = Field(..., min_length=3, max_length=255)
    semestre: int = Field(..., ge=1, le=10, example=1)


class MateriaCreate(MateriaBase):
    pass


class MateriaResponse(MateriaBase):
    """Schema para respuesta de Materia"""
    id: int
    carrera_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MateriaDetailResponse(MateriaResponse):
    """Schema detallado de Materia"""
    carrera: Optional[CarreraResponse] = None


# Actualizar referencias forward
CarreraDetailResponse.model_rebuild()
MateriaDetailResponse.model_rebuild()
