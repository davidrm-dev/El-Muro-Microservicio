"""
Tests unitarios para el servicio de materias
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.services.materia_service import CarrerasServiceClient


# Configurar base de datos de prueba
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Resetear la base de datos antes de cada test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def mock_carrera_exists(monkeypatch):
    """Evitar dependencia de carreras-service durante pruebas unitarias"""
    monkeypatch.setattr(CarrerasServiceClient, "carrera_exists", staticmethod(lambda _carrera_id: True))


class TestMaterias:
    """Tests para el endpoint de materias"""
    
    def test_health_check(self):
        """Test del health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_crear_materia(self):
        """Test para crear una materia"""
        response = client.post(
            "/api/materias/crear",
            headers={"x-role": "ADMIN"},
            json={
                "nombre": "Programación I",
                "semestre": 1,
                "carrera_id": 1,
                "descripcion": "Test materia"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Programación I"
        assert data["id"] is not None
    
    def test_obtener_materias(self):
        """Test para obtener todas las materias"""
        # Crear una materia primero
        client.post(
            "/api/materias/crear",
            headers={"x-role": "ADMIN"},
            json={
                "nombre": "Test Materia",
                "semestre": 1,
                "carrera_id": 1
            }
        )
        
        response = client.get(
            "/api/materias/",
            headers={"x-role": "ESTUDIANTE"}
        )
        assert response.status_code == 200
        assert len(response.json()) > 0
    
    def test_obtener_materia_by_id(self):
        """Test para obtener una materia por ID"""
        # Crear materia
        create_response = client.post(
            "/api/materias/crear",
            headers={"x-role": "ADMIN"},
            json={
                "nombre": "Test Materia",
                "semestre": 1,
                "carrera_id": 1
            }
        )
        materia_id = create_response.json()["id"]
        
        response = client.get(
            f"/api/materias/{materia_id}",
            headers={"x-role": "ESTUDIANTE"}
        )
        assert response.status_code == 200
        assert response.json()["id"] == materia_id
    
    def test_actualizar_materia(self):
        """Test para actualizar una materia"""
        # Crear materia
        create_response = client.post(
            "/api/materias/crear",
            headers={"x-role": "ADMIN"},
            json={
                "nombre": "Test Materia",
                "semestre": 1,
                "carrera_id": 1
            }
        )
        materia_id = create_response.json()["id"]
        
        # Actualizar
        response = client.put(
            f"/api/materias/{materia_id}",
            headers={"x-role": "ADMIN"},
            json={"nombre": "Test Actualizado"}
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Test Actualizado"
    
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
