"""
Script para popular la base de datos con datos iniciales
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.materia import Materia, Tema


def seed_database():
    """Poblar la base de datos con datos iniciales"""
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Listar materias existentes
        existing_materias = db.query(Materia).count()
        
        if existing_materias > 0:
            print("La base de datos ya contiene datos. Saltando seed...")
            return
        
        # Crear materias
        materias_data = [
            {
                "nombre": "Programación I",
                "descripcion": "Introducción a la programación",
                "semestre": 1,
                "carrera_id": 1
            },
            {
                "nombre": "Matemáticas Discretas",
                "descripcion": "Matemáticas para informática",
                "semestre": 1,
                "carrera_id": 1
            },
            {
                "nombre": "Estructuras de Datos",
                "descripcion": "Aprendizaje de estructuras de datos",
                "semestre": 2,
                "carrera_id": 1
            },
            {
                "nombre": "Base de Datos",
                "descripcion": "Diseño y gestión de bases de datos",
                "semestre": 3,
                "carrera_id": 1
            },
            {
                "nombre": "Circuitos I",
                "descripcion": "Circuitos eléctricos básicos",
                "semestre": 1,
                "carrera_id": 2
            },
        ]
        
        materias = []
        for materia_data in materias_data:
            materia = Materia(**materia_data)
            db.add(materia)
            materias.append(materia)
        
        db.commit()
        
        # Crear temas para algunas materias
        temas_data = [
            {
                "nombre": "Variables y Tipos de Datos",
                "descripcion": "Entender variables y tipos de datos",
                "materia_id": 1
            },
            {
                "nombre": "Funciones",
                "descripcion": "Definición y uso de funciones",
                "materia_id": 1
            },
            {
                "nombre": "Lógica Proposicional",
                "descripcion": "Introducción a la lógica",
                "materia_id": 2
            },
            {
                "nombre": "Árboles",
                "descripcion": "Estructura de datos árbol",
                "materia_id": 3
            },
            {
                "nombre": "Grafos",
                "descripcion": "Estructura de datos grafo",
                "materia_id": 3
            },
        ]
        
        for tema_data in temas_data:
            tema = Tema(**tema_data)
            db.add(tema)
        
        db.commit()
        print("✅ Base de datos poblada exitosamente")
        print(f"   - {len(materias)} materias creadas")
        print(f"   - {len(temas_data)} temas creados")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al poblar la base de datos: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
