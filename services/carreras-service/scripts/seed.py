"""
Script para popular la base de datos con datos iniciales
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.carrera import Carrera


def seed_database():
    """Poblar la base de datos con datos iniciales"""
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Listar carreras existentes
        existing_carreras = db.query(Carrera).count()
        
        if existing_carreras > 0:
            print("La base de datos ya contiene datos. Saltando seed...")
            return
        
        # Crear carreras
        carreras_data = [
            {
                "nombre": "Ingeniería de Sistemas",
                "descripcion": "Carrera enfocada en sistemas computacionales, programación y tecnología de la información"
            },
            {
                "nombre": "Ingeniería Electrónica",
                "descripcion": "Carrera especializada en electrónica, circuitos y sistemas electrónicos"
            },
            {
                "nombre": "Ingeniería Industrial",
                "descripcion": "Carrera enfocada en optimización de procesos y gestión empresarial"
            }
        ]
        
        carreras = []
        for carrera_data in carreras_data:
            carrera = Carrera(**carrera_data)
            db.add(carrera)
            carreras.append(carrera)
        
        db.commit()
        
        db.commit()
        print("✅ Base de datos poblada exitosamente")
        print(f"   - {len(carreras)} carreras creadas")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al poblar la base de datos: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
