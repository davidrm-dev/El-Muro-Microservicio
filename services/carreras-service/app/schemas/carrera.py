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


class MateriaResponse(BaseModel):
    """Resumen de materia obtenido desde materias-service"""
    id: int
    nombre: str
    descripcion: Optional[str] = None
    semestre: int
    carrera_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Actualizar referencias forward
CarreraDetailResponse.model_rebuild()
