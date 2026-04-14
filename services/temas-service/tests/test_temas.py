from __future__ import annotations

from typing import Any

import jwt
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.repositories.tema_repository import InMemoryTemaRepository
from app.routers.temas import get_materias_client, get_posts_client, get_tema_repository
from app.services.external_clients import MateriasClient, PostsClient


class FakeMateriasClient(MateriasClient):
    def __init__(self, existing_ids: set[int]) -> None:
        self.existing_ids = existing_ids

    def ensure_materia_exists(self, materia_id: int, authorization: str | None) -> None:
        if materia_id not in self.existing_ids:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail=f"Materia {materia_id} not found")


class FakePostsClient(PostsClient):
    def __init__(self, posts_by_tema: dict[str, list[dict[str, Any]]]) -> None:
        self.posts_by_tema = posts_by_tema

    def get_posts_by_tema(self, tema_id: str, authorization: str | None) -> list[dict[str, Any]]:
        return self.posts_by_tema.get(tema_id, [])


def build_token(role: str, user_id: str = "user-1") -> str:
    settings = get_settings()
    return jwt.encode(
        {"userId": user_id, "rol": role},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def build_headers(role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {build_token(role)}"}


def setup_test_client() -> tuple[TestClient, InMemoryTemaRepository]:
    repository = InMemoryTemaRepository()
    app.dependency_overrides[get_tema_repository] = lambda: repository
    app.dependency_overrides[get_materias_client] = lambda: FakeMateriasClient({10, 20})
    app.dependency_overrides[get_posts_client] = lambda: FakePostsClient(
        {"1": [{"id": "post-1", "titulo": "Apuntes de algebra", "temaId": "1"}]}
    )
    return TestClient(app), repository


def teardown_overrides() -> None:
    app.dependency_overrides.clear()


def test_admin_can_create_and_list_temas() -> None:
    client, _ = setup_test_client()

    response = client.post(
        "/api/temas",
        headers=build_headers("admin"),
        json={"nombre": "Matrices", "descripcion": "Tema base", "materia_id": 10},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["nombre"] == "Matrices"
    assert payload["esta_activo"] is True

    list_response = client.get("/api/temas?materia_id=10", headers=build_headers("estudiante"))
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    teardown_overrides()


def test_create_fails_when_materia_does_not_exist() -> None:
    client, _ = setup_test_client()

    response = client.post(
        "/api/temas",
        headers=build_headers("admin"),
        json={"nombre": "Matrices", "descripcion": "Tema base", "materia_id": 999},
    )

    assert response.status_code == 404
    teardown_overrides()


def test_student_cannot_create_tema() -> None:
    client, _ = setup_test_client()

    response = client.post(
        "/api/temas",
        headers=build_headers("estudiante"),
        json={"nombre": "Matrices", "descripcion": "Tema base", "materia_id": 10},
    )

    assert response.status_code == 403
    teardown_overrides()


def test_admin_can_disable_tema() -> None:
    client, repository = setup_test_client()
    tema = repository.create({"nombre": "Vectores", "descripcion": None, "materia_id": 10})

    response = client.patch(f"/api/temas/{tema['id']}/disable", headers=build_headers("admin"))

    assert response.status_code == 200
    assert response.json()["esta_activo"] is False
    teardown_overrides()


def test_can_get_posts_for_tema() -> None:
    client, repository = setup_test_client()
    tema = repository.create({"nombre": "Limites", "descripcion": None, "materia_id": 10})

    response = client.get(f"/api/temas/{tema['id']}/posts", headers=build_headers("estudiante"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["tema"]["id"] == tema["id"]
    assert payload["posts"][0]["id"] == "post-1"
    teardown_overrides()
