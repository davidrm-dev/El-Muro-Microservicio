from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.carrera import Carrera
from app.schemas.carrera import CarreraCreate, CarreraUpdate
from fastapi import HTTPException
import httpx
import logging

logger = logging.getLogger(__name__)


class MateriasServiceClient:
    """Cliente para comunicarse con el servicio de materias"""
    
    @staticmethod
    def delete_materias_by_carrera(carrera_id: int) -> bool:
        """Eliminir todas las materias de una carrera en materias-service"""
        try:
            # URL del endpoint interno en materias-service
            materias_url = f"http://materias-service:8002/api/materias/carrera/{carrera_id}/all"
            
            with httpx.Client(timeout=5.0) as client:
                response = client.delete(materias_url)
                if response.status_code == 200:
                    logger.info(f"Materias de carrera {carrera_id} eliminadas en materias-service")
                    return True
                else:
                    logger.warning(f"Error al eliminar materias: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Error eliminando materias en materias-service: {str(e)}")
            # Continuar incluso si falla, ya que la carrera se elimina localmente
            return False


class CarreraService:
    """Servicio para operaciones de Carrera"""
    
    @staticmethod
    def create_carrera(db: Session, carrera_data: CarreraCreate) -> Carrera:
        """Crear una nueva carrera"""
        # Verificar si ya existe una carrera con el mismo nombre
        existing = db.query(Carrera).filter(
            func.lower(Carrera.nombre) == func.lower(carrera_data.nombre)
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Carrera con nombre '{carrera_data.nombre}' ya existe"
            )
        
        db_carrera = Carrera(
            nombre=carrera_data.nombre.strip(),
            descripcion=carrera_data.descripcion
        )
        db.add(db_carrera)
        db.commit()
        db.refresh(db_carrera)
        return db_carrera
    
    @staticmethod
    def get_carrera_by_id(db: Session, carrera_id: int) -> Carrera:
        """Obtener una carrera por ID"""
        carrera = db.query(Carrera).filter(Carrera.id == carrera_id).first()
        if not carrera:
            raise HTTPException(status_code=404, detail="Carrera no encontrada")
        return carrera
    
    @staticmethod
    def get_all_carreras(db: Session, skip: int = 0, limit: int = 100) -> list[Carrera]:
        """Obtener todas las carreras"""
        return db.query(Carrera).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_carrera(db: Session, carrera_id: int, carrera_data: CarreraUpdate) -> Carrera:
        """Actualizar una carrera"""
        carrera = CarreraService.get_carrera_by_id(db, carrera_id)
        
        # Verificar si el nuevo nombre ya existe
        if carrera_data.nombre:
            existing = db.query(Carrera).filter(
                func.lower(Carrera.nombre) == func.lower(carrera_data.nombre),
                Carrera.id != carrera_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe una carrera con el nombre '{carrera_data.nombre}'"
                )
        
        # Actualizar campos
        update_data = carrera_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(carrera, field, value)
        
        db.commit()
        db.refresh(carrera)
        return carrera
    
    @staticmethod
    def delete_carrera(db: Session, carrera_id: int) -> dict:
        """Eliminar una carrera y todas sus materias (locales y en materias-service)"""
        carrera = CarreraService.get_carrera_by_id(db, carrera_id)
        carrera_nombre = carrera.nombre
        
        # Paso 1: Eliminar materias en materias-service (si existe el servicio)
        MateriasServiceClient.delete_materias_by_carrera(carrera_id)
        
        # Paso 2: Eliminar la carrera localmente (cascada eliminará materias locales)
        db.delete(carrera)
        db.commit()
        
        return {
            "message": f"Carrera '{carrera_nombre}' eliminada exitosamente (incluyendo todas sus materias)",
            "deleted_carrera_id": carrera_id
        }
    
    @staticmethod
    def get_carrera_count(db: Session) -> int:
        """Obtener cantidad total de carreras"""
        return db.query(func.count(Carrera.id)).scalar()
