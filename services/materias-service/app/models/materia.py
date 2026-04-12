from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Materia(Base):
    """Modelo de Materia"""
    __tablename__ = "materias"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    semestre = Column(Integer, nullable=False, index=True)
    carrera_id = Column(Integer, nullable=False, index=True)  # No es FK, se valida por API
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con Tema (será creada cuando temas-service exista)
    temas = relationship("Tema", back_populates="materia", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index("idx_materia_nombre", "nombre"),
        Index("idx_materia_carrera_id", "carrera_id"),
        Index("idx_materia_semestre", "semestre"),
    )
    
    def __repr__(self):
        return f"<Materia(id={self.id}, nombre='{self.nombre}', semestre={self.semestre})>"


class Tema(Base):
    """Modelo de Tema (estructura lista para ser servicio independiente)"""
    __tablename__ = "temas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    materia_id = Column(Integer, ForeignKey("materias.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con Materia
    materia = relationship("Materia", back_populates="temas")
    
    # Índices
    __table_args__ = (
        Index("idx_tema_nombre", "nombre"),
        Index("idx_tema_materia", "materia_id"),
    )
    
    def __repr__(self):
        return f"<Tema(id={self.id}, nombre='{self.nombre}')>"
