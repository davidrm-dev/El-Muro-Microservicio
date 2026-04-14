from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_admin, require_any_role
from app.schemas.materia import MateriaCreate, MateriaUpdate, MateriaResponse, MateriaDetailResponse
from app.services.materia_service import MateriaService

router = APIRouter(
    prefix="/api/materias",
    tags=["materias"],
)


# ==================== Endpoints de Materias ====================

@router.post("/crear", response_model=MateriaResponse, status_code=201)
def crear_materia(
    materia_data: MateriaCreate,
    db: Session = Depends(get_db),
    role: str = Depends(require_admin)
):
    """
    Crear una nueva materia (Solo ADMIN)
    
    - **nombre**: Nombre de la materia
    - **semestre**: Semestre en el que se dicta (1-10)
    - **carrera_id**: ID de la carrera a la que pertenece
    - **descripcion**: Descripción opcional
    """
    return MateriaService.create_materia(db, materia_data)


@router.get("/", response_model=list[MateriaResponse])
def obtener_materias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    carrera_id: int = Query(None),
    db: Session = Depends(get_db),
    role: str = Depends(require_any_role)
):
    """
    Obtener todas las materias (Cualquier rol autenticado)
    
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    - **carrera_id**: Opcional - Filtrar por carrera
    """
    if carrera_id:
        return MateriaService.get_materias_by_carrera(db, carrera_id, skip, limit)
    return MateriaService.get_all_materias(db, skip, limit)


@router.get("/carrera/{carrera_id}", response_model=list[MateriaResponse])
def obtener_materias_por_carrera(
    carrera_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    role: str = Depends(require_any_role)
):
    """
    Obtener todas las materias de una carrera específica (Cualquier rol)
    
    - **carrera_id**: ID de la carrera
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    """
    return MateriaService.get_materias_by_carrera(db, carrera_id, skip, limit)


@router.get("/{materia_id}", response_model=MateriaDetailResponse)
def obtener_materia(
    materia_id: int,
    db: Session = Depends(get_db),
    role: str = Depends(require_any_role)
):
    """
    Obtener una materia específica (Cualquier rol)
    """
    return MateriaService.get_materia_by_id(db, materia_id)


@router.put("/{materia_id}", response_model=MateriaResponse)
def actualizar_materia(
    materia_id: int,
    materia_data: MateriaUpdate,
    db: Session = Depends(get_db),
    role: str = Depends(require_admin)
):
    """
    Actualizar una materia (Solo ADMIN)
    """
    return MateriaService.update_materia(db, materia_id, materia_data)


@router.delete("/{materia_id}")
def eliminar_materia(
    materia_id: int,
    db: Session = Depends(get_db),
    role: str = Depends(require_admin)
):
    """
    Eliminar una materia (Solo ADMIN)
    """
    return MateriaService.delete_materia(db, materia_id)


@router.delete("/carrera/{carrera_id}/all")
def eliminar_materias_por_carrera(
    carrera_id: int,
    db: Session = Depends(get_db)
):
    """
    Endpoint INTERNO: Eliminar todas las materias de una carrera
    (Llamado automáticamente por carreras-service cuando se elimina una carrera)
    
    Sin autenticación requerida - Solo para comunicación interna entre servicios
    """
    return MateriaService.delete_materias_by_carrera(db, carrera_id)


