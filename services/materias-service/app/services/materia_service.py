from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.materia import Materia
from app.schemas.materia import MateriaCreate, MateriaUpdate
from app.core.config import get_settings
from app.core.service_discovery import discover_service_url
from fastapi import HTTPException
import httpx
import logging

logger = logging.getLogger(__name__)


class CarrerasServiceClient:
    """Cliente para consultar el servicio de carreras"""
    
    @staticmethod
    def _base_url() -> str:
        settings = get_settings()
        return discover_service_url(settings.carreras_service_name, settings.eureka_server).rstrip("/")

    @staticmethod
    def carrera_exists(carrera_id: int) -> bool:
        """Verificar si una carrera existe en el servicio de carreras"""
        try:
            carreras_url = f"{CarrerasServiceClient._base_url()}/api/carreras/_exists/{carrera_id}"
            
            with httpx.Client(timeout=5.0) as client:
                response = client.get(carreras_url)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("exists", False)
                return False
        except Exception as e:
            logger.error(f"Error verificando carrera {carrera_id}: {str(e)}")
            # Si no podemos conectar, asumir que la carrera NO existe
            return False


class MateriaService:
    """Servicio para operaciones de Materia"""
    
    @staticmethod
    def create_materia(db: Session, materia_data: MateriaCreate) -> Materia:
        """Crear una nueva materia"""
        # Validar que la carrera existe en el servicio de carreras
        if not CarrerasServiceClient.carrera_exists(materia_data.carrera_id):
            raise HTTPException(
                status_code=404, 
                detail="Carrera no encontrada"
            )
        
        db_materia = Materia(
            nombre=materia_data.nombre.strip(),
            descripcion=materia_data.descripcion,
            semestre=materia_data.semestre,
            carrera_id=materia_data.carrera_id
        )
        db.add(db_materia)
        db.commit()
        db.refresh(db_materia)
        return db_materia
    
    @staticmethod
    def get_materia_by_id(db: Session, materia_id: int) -> Materia:
        """Obtener una materia por ID"""
        materia = db.query(Materia).filter(Materia.id == materia_id).first()
        if not materia:
            raise HTTPException(status_code=404, detail="Materia no encontrada")
        return materia
    
    @staticmethod
    def get_all_materias(db: Session, skip: int = 0, limit: int = 100) -> list[Materia]:
        """Obtener todas las materias"""
        return db.query(Materia).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_materias_by_carrera(db: Session, carrera_id: int, skip: int = 0, limit: int = 100) -> list[Materia]:
        """Obtener todas las materias de una carrera"""
        return db.query(Materia).filter(
            Materia.carrera_id == carrera_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_materia(db: Session, materia_id: int, materia_data: MateriaUpdate) -> Materia:
        """Actualizar una materia"""
        materia = MateriaService.get_materia_by_id(db, materia_id)
        
        # Actualizar campos
        update_data = materia_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(materia, field, value)
        
        db.commit()
        db.refresh(materia)
        return materia
    
    @staticmethod
    def delete_materia(db: Session, materia_id: int) -> dict:
        """Eliminar una materia"""
        materia = MateriaService.get_materia_by_id(db, materia_id)
        db.delete(materia)
        db.commit()
        return {"message": "Materia eliminada exitosamente"}
    
    @staticmethod
    def delete_materias_by_carrera(db: Session, carrera_id: int) -> dict:
        """Eliminar todas las materias de una carrera (llamado por carreras-service)"""
        materias = db.query(Materia).filter(Materia.carrera_id == carrera_id).all()
        count = len(materias)
        for materia in materias:
            db.delete(materia)
        db.commit()
        return {
            "message": f"Se eliminaron {count} materia(s) de la carrera",
            "deleted_count": count
        }
    
    @staticmethod
    def get_materia_count(db: Session) -> int:
        """Obtener cantidad total de materias"""
        return db.query(func.count(Materia.id)).scalar()
