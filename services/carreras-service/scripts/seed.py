"""
Script para popular la base de datos con datos iniciales
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.carrera import Carrera
from app.models.materia import Materia


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
        
        # Crear materias para cada carrera
        materias_data = {
            1: [  # Ingeniería de Sistemas
                {"nombre": "Programación I", "semestre": 1},
                {"nombre": "Matemáticas Discretas", "semestre": 1},
                {"nombre": "Programación II", "semestre": 2},
                {"nombre": "Estructuras de Datos", "semestre": 2},
                {"nombre": "Base de Datos", "semestre": 3},
                {"nombre": "Desarrollo Web", "semestre": 4},
                {"nombre": "Sistemas Operativos", "semestre": 5},
                {"nombre": "Redes de Computadores", "semestre": 5},
            ],
            2: [  # Ingeniería Electrónica
                {"nombre": "Circuitos I", "semestre": 1},
                {"nombre": "Electromagnetismo", "semestre": 1},
                {"nombre": "Circuitos II", "semestre": 2},
                {"nombre": "Electrónica Analógica", "semestre": 3},
                {"nombre": "Electrónica Digital", "semestre": 4},
                {"nombre": "Procesamiento de Señales", "semestre": 5},
            ],
            3: [  # Ingeniería Industrial
                {"nombre": "Administración", "semestre": 1},
                {"nombre": "Contabilidad", "semestre": 1},
                {"nombre": "Investigación de Operaciones", "semestre": 3},
                {"nombre": "Gestión de Proyectos", "semestre": 5},
            ]
        }
        
        for carrera_id, materias in materias_data.items():
            for materia_data in materias:
                materia = Materia(
                    carrera_id=carrera_id,
                    **materia_data
                )
                db.add(materia)
        
        db.commit()
        print("✅ Base de datos poblada exitosamente")
        print(f"   - {len(carreras)} carreras creadas")
        print(f"   - {sum(len(m) for m in materias_data.values())} materias creadas")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al poblar la base de datos: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
