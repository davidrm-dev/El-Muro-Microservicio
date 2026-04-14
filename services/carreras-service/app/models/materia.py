from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Materia(Base):
    """Modelo de Materia"""
    __tablename__ = "materias"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    semestre = Column(Integer, nullable=False, index=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con Carrera
    carrera = relationship("Carrera", back_populates="materias")
    
    # Índices
    __table_args__ = (
        Index("idx_materia_carrera", "carrera_id"),
        Index("idx_materia_semestre", "semestre"),
    )
    
    def __repr__(self):
        return f"<Materia(id={self.id}, nombre='{self.nombre}', semestre={self.semestre})>"
