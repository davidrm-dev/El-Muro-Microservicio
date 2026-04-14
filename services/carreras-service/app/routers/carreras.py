from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_admin, require_any_role
from app.schemas.carrera import CarreraCreate, CarreraUpdate, CarreraResponse, CarreraDetailResponse
from app.services.carrera_service import CarreraService

router = APIRouter(
    prefix="/api/carreras",
    tags=["carreras"],
)


@router.post("/crear", response_model=CarreraResponse, status_code=201)
def crear_carrera(
    carrera_data: CarreraCreate,
    db: Session = Depends(get_db),
    role: str = Depends(require_admin)
):
    """
    Crear una nueva carrera (Solo ADMIN)
    
    - **nombre**: Nombre único de la carrera
    - **descripcion**: Descripción opcional
    """
    return CarreraService.create_carrera(db, carrera_data)


@router.get("/", response_model=list[CarreraResponse])
def obtener_carreras(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    role: str = Depends(require_any_role)
):
    """
    Obtener todas las carreras (Cualquier rol autenticado)
    
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    """
    return CarreraService.get_all_carreras(db, skip, limit)


@router.get("/_exists/{carrera_id}")
def existe_carrera(
    carrera_id: int,
    db: Session = Depends(get_db)
):
    """
    Verificar si una carrera existe (Endpoint público para validación interna)
    Retorna {"exists": true} o {"exists": false}
    """
    try:
        carrera = CarreraService.get_carrera_by_id(db, carrera_id)
        return {"exists": True}
    except:
        return {"exists": False}


@router.get("/{carrera_id}", response_model=CarreraDetailResponse)
def obtener_carrera(
    carrera_id: int,
    db: Session = Depends(get_db),
    role: str = Depends(require_any_role)
):
    """
    Obtener una carrera específica con sus materias (Cualquier rol)
    """
    return CarreraService.get_carrera_by_id(db, carrera_id)


@router.put("/{carrera_id}", response_model=CarreraResponse)
def actualizar_carrera(
    carrera_id: int,
    carrera_data: CarreraUpdate,
    db: Session = Depends(get_db),
    role: str = Depends(require_admin)
):
    """
    Actualizar una carrera (Solo ADMIN)
    """
    return CarreraService.update_carrera(db, carrera_id, carrera_data)


@router.delete("/{carrera_id}")
def eliminar_carrera(
    carrera_id: int,
    db: Session = Depends(get_db),
    role: str = Depends(require_admin)
):
    """
    Eliminar una carrera (Solo ADMIN)
    """
    return CarreraService.delete_carrera(db, carrera_id)
