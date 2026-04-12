from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.carrera import Carrera
from app.schemas.carrera import CarreraCreate, CarreraUpdate
from fastapi import HTTPException


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
        """Eliminar una carrera"""
        carrera = CarreraService.get_carrera_by_id(db, carrera_id)
        db.delete(carrera)
        db.commit()
        return {"message": "Carrera eliminada exitosamente"}
    
    @staticmethod
    def get_carrera_count(db: Session) -> int:
        """Obtener cantidad total de carreras"""
        return db.query(func.count(Carrera.id)).scalar()
