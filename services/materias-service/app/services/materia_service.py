from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.materia import Materia, Tema
from app.schemas.materia import MateriaCreate, MateriaUpdate, TemaCreate
from app.core.external_services import CarrerasServiceClient
from fastapi import HTTPException


class MateriaService:
    """Servicio para operaciones de Materia"""
    
    @staticmethod
    def create_materia(db: Session, materia_data: MateriaCreate) -> Materia:
        """Crear una nueva materia"""
        # Validar que la carrera existe ANTES de crear la materia
        # Esto es opcional - puede validarse solo por FK o por llamada a API
        # Por ahora, usamos FK pero dejamos el código para validar por API
        
        # Opción 1: Validar por API (comentada)
        # if not CarrerasServiceClient.carrera_exists(materia_data.carrera_id):
        #     raise HTTPException(status_code=404, detail="Carrera no encontrada")
        
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
    def get_materia_count(db: Session) -> int:
        """Obtener cantidad total de materias"""
        return db.query(func.count(Materia.id)).scalar()


class TemaService:
    """Servicio para operaciones de Tema"""
    
    @staticmethod
    def create_tema(db: Session, materia_id: int, tema_data: TemaCreate) -> Tema:
        """Crear un nuevo tema"""
        # Verificar que la materia existe
        materia = db.query(Materia).filter(Materia.id == materia_id).first()
        if not materia:
            raise HTTPException(status_code=404, detail="Materia no encontrada")
        
        db_tema = Tema(
            nombre=tema_data.nombre.strip(),
            descripcion=tema_data.descripcion,
            materia_id=materia_id
        )
        db.add(db_tema)
        db.commit()
        db.refresh(db_tema)
        return db_tema
    
    @staticmethod
    def get_tema_by_id(db: Session, tema_id: int) -> Tema:
        """Obtener un tema por ID"""
        tema = db.query(Tema).filter(Tema.id == tema_id).first()
        if not tema:
            raise HTTPException(status_code=404, detail="Tema no encontrado")
        return tema
    
    @staticmethod
    def get_temas_by_materia(db: Session, materia_id: int) -> list[Tema]:
        """Obtener todos los temas de una materia"""
        # Verificar que la materia existe
        materia = db.query(Materia).filter(Materia.id == materia_id).first()
        if not materia:
            raise HTTPException(status_code=404, detail="Materia no encontrada")
        
        return db.query(Tema).filter(Tema.materia_id == materia_id).all()
    
    @staticmethod
    def delete_tema(db: Session, tema_id: int) -> dict:
        """Eliminar un tema"""
        tema = TemaService.get_tema_by_id(db, tema_id)
        db.delete(tema)
        db.commit()
        return {"message": "Tema eliminado exitosamente"}
