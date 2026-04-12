"""
Tests unitarios para el servicio de carreras
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db


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


class TestCarreras:
    """Tests para el endpoint de carreras"""
    
    def test_health_check(self):
        """Test del health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_crear_carrera(self):
        """Test para crear una carrera"""
        response = client.post(
            "/api/carreras/crear",
            headers={"x-role": "ADMIN"},
            json={
                "nombre": "Ingeniería de Sistemas",
                "descripcion": "Test carrera"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Ingeniería de Sistemas"
        assert data["id"] is not None
    
    def test_obtener_carreras(self):
        """Test para obtener todas las carreras"""
        # Crear una carrera primero
        client.post(
            "/api/carreras/crear",
            headers={"x-role": "ADMIN"},
            json={
                "nombre": "Test Carrera",
                "descripcion": "Test"
            }
        )
        
        response = client.get(
            "/api/carreras/",
            headers={"x-role": "ESTUDIANTE"}
        )
        assert response.status_code == 200
        assert len(response.json()) > 0
    
    def test_obtener_carrera_by_id(self):
        """Test para obtener una carrera por ID"""
        # Crear carrera
        create_response = client.post(
            "/api/carreras/crear",
            headers={"x-role": "ADMIN"},
            json={"nombre": "Test Carrera", "descripcion": "Test"}
        )
        carrera_id = create_response.json()["id"]
        
        response = client.get(
            f"/api/carreras/{carrera_id}",
            headers={"x-role": "ESTUDIANTE"}
        )
        assert response.status_code == 200
        assert response.json()["id"] == carrera_id
    
    def test_actualizar_carrera(self):
        """Test para actualizar una carrera"""
        # Crear carrera
        create_response = client.post(
            "/api/carreras/crear",
            headers={"x-role": "ADMIN"},
            json={"nombre": "Test Carrera", "descripcion": "Test"}
        )
        carrera_id = create_response.json()["id"]
        
        # Actualizar
        response = client.put(
            f"/api/carreras/{carrera_id}",
            headers={"x-role": "ADMIN"},
            json={"nombre": "Test Actualizado"}
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Test Actualizado"
    
    def test_eliminar_carrera(self):
        """Test para eliminar una carrera"""
        # Crear carrera
        create_response = client.post(
            "/api/carreras/crear",
            headers={"x-role": "ADMIN"},
            json={"nombre": "Test Carrera", "descripcion": "Test"}
        )
        carrera_id = create_response.json()["id"]
        
        # Eliminar
        response = client.delete(
            f"/api/carreras/{carrera_id}",
            headers={"x-role": "ADMIN"}
        )
        assert response.status_code == 200
        
        # Verificar que se eliminó
        get_response = client.get(
            f"/api/carreras/{carrera_id}",
            headers={"x-role": "ESTUDIANTE"}
        )
        assert get_response.status_code == 404
    
    def test_no_permission_without_role(self):
        """Test que falla sin proporcionar rol"""
        response = client.post(
            "/api/carreras/crear",
            json={"nombre": "Test", "descripcion": "Test"}
        )
        assert response.status_code == 401
    
    def test_estudiante_cannot_create(self):
        """Test que estudiante no puede crear carrera"""
        response = client.post(
            "/api/carreras/crear",
            headers={"x-role": "ESTUDIANTE"},
            json={"nombre": "Test", "descripcion": "Test"}
        )
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
