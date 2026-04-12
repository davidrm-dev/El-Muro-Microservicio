from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Carrera(Base):
    """Modelo de Carrera"""
    __tablename__ = "carreras"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con Materiasget_db
    materias = relationship("Materia", back_populates="carrera", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index("idx_carrera_nombre", "nombre"),
    )
    
    def __repr__(self):
        return f"<Carrera(id={self.id}, nombre='{self.nombre}')>"
