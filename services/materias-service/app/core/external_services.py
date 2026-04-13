import requests
from app.core.config import get_settings

settings = get_settings()


class CarrerasServiceClient:
    """Cliente para comunicarse con el servicio de carreras"""
    
    BASE_URL = settings.carreras_service_url
    TIMEOUT = 5  # segundos
    
    @staticmethod
    def get_carrera(carrera_id: int) -> dict:
        """Obtener una carrera del servicio de carreras"""
        try:
            url = f"{CarrerasServiceClient.BASE_URL}/api/carreras/{carrera_id}"
            response = requests.get(url, timeout=CarrerasServiceClient.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error comunicándose con carreras-service: {e}")
            return None
    
    @staticmethod
    def carrera_exists(carrera_id: int) -> bool:
        """Verificar si una carrera existe"""
        carrera = CarrerasServiceClient.get_carrera(carrera_id)
        return carrera is not None
