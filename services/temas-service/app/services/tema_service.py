from __future__ import annotations

from fastapi import HTTPException

from app.repositories.tema_repository import TemaRepository
from app.schemas.tema import TemaCreate, TemaUpdate
from app.services.external_clients import MateriasClient, PostsClient


class TemaService:
    def __init__(
        self,
        repository: TemaRepository,
        materias_client: MateriasClient,
        posts_client: PostsClient,
    ) -> None:
        self.repository = repository
        self.materias_client = materias_client
        self.posts_client = posts_client

    def create_tema(self, payload: TemaCreate, authorization: str | None) -> dict:
        self.materias_client.ensure_materia_exists(payload.materia_id, authorization)
        return self.repository.create(payload.model_dump())

    def list_temas(self, materia_id: int | None, include_inactive: bool) -> list[dict]:
        return self.repository.list(materia_id=materia_id, include_inactive=include_inactive)

    def get_tema(self, tema_id: str) -> dict:
        tema = self.repository.get_by_id(tema_id)
        if tema is None:
            raise HTTPException(status_code=404, detail="Tema not found")
        return tema

    def update_tema(self, tema_id: str, payload: TemaUpdate, authorization: str | None) -> dict:
        if payload.materia_id is not None:
            self.materias_client.ensure_materia_exists(payload.materia_id, authorization)

        tema = self.repository.update(tema_id, payload.model_dump(exclude_unset=True))
        if tema is None:
            raise HTTPException(status_code=404, detail="Tema not found")
        return tema

    def disable_tema(self, tema_id: str) -> dict:
        tema = self.repository.disable(tema_id)
        if tema is None:
            raise HTTPException(status_code=404, detail="Tema not found")
        return tema

    def get_posts_for_tema(self, tema_id: str, authorization: str | None) -> dict:
        tema = self.get_tema(tema_id)
        posts = self.posts_client.get_posts_by_tema(tema_id, authorization)
        return {
            "tema": tema,
            "posts": posts,
        }
