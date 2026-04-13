from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_admin, require_any_role
from app.schemas.carrera import MateriaCreate, MateriaResponse
from app.services.materia_service import MateriaService

router = APIRouter(
    prefix="/api/carreras",
    tags=["materias"],
)


@router.post("/{carrera_id}/materias", response_model=MateriaResponse, status_code=201)
def crear_materia(
    carrera_id: int,
    materia_data: MateriaCreate,
    db: Session = Depends(get_db),
    role: str = Depends(require_admin)
):
    """
    Crear una nueva materia en una carrera (Solo ADMIN)
    
    - **carrera_id**: ID de la carrera
    - **nombre**: Nombre de la materia
    - **semestre**: Semestre en el que se dicta (1-10)
    """
    return MateriaService.create_materia(db, carrera_id, materia_data)


@router.get("/{carrera_id}/materias", response_model=list[MateriaResponse])
def obtener_materias_carrera(
    carrera_id: int,
    db: Session = Depends(get_db),
    role: str = Depends(require_any_role)
):
    """
    Obtener todas las materias de una carrera (Cualquier rol)
    
    - **carrera_id**: ID de la carrera
    """
    return MateriaService.get_materias_by_carrera(db, carrera_id)
