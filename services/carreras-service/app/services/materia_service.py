from sqlalchemy.orm import Session
from app.models.carrera import Carrera
from app.models.materia import Materia
from app.schemas.carrera import MateriaCreate, MateriaResponse
from fastapi import HTTPException


class MateriaService:
    """Servicio para operaciones de Materia"""
    
    @staticmethod
    def create_materia(db: Session, carrera_id: int, materia_data: MateriaCreate) -> Materia:
        """Crear una nueva materia"""
        # Verificar que la carrera exista
        carrera = db.query(Carrera).filter(Carrera.id == carrera_id).first()
        if not carrera:
            raise HTTPException(status_code=404, detail="Carrera no encontrada")
        
        # Crear materia
        db_materia = Materia(
            nombre=materia_data.nombre.strip(),
            semestre=materia_data.semestre,
            carrera_id=carrera_id
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
    def get_materias_by_carrera(db: Session, carrera_id: int) -> list[Materia]:
        """Obtener todas las materias de una carrera"""
        # Verificar que la carrera exista
        carrera = db.query(Carrera).filter(Carrera.id == carrera_id).first()
        if not carrera:
            raise HTTPException(status_code=404, detail="Carrera no encontrada")
        
        return db.query(Materia).filter(Materia.carrera_id == carrera_id).all()
    
    @staticmethod
    def get_all_materias(db: Session, skip: int = 0, limit: int = 100) -> list[Materia]:
        """Obtener todas las materias"""
        return db.query(Materia).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_materia(db: Session, materia_id: int, materia_data: MateriaCreate) -> Materia:
        """Actualizar una materia"""
        materia = MateriaService.get_materia_by_id(db, materia_id)
        
        materia.nombre = materia_data.nombre.strip()
        materia.semestre = materia_data.semestre
        
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
