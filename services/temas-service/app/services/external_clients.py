from __future__ import annotations

from typing import Any

import requests
from fastapi import HTTPException

from app.core.config import get_settings


class MateriasClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.materias_service_url).rstrip("/")
        self.timeout = timeout or settings.request_timeout_seconds

    def ensure_materia_exists(self, materia_id: int, authorization: str | None) -> None:
        headers = {"Authorization": authorization} if authorization else {}
        try:
            response = requests.get(
                f"{self.base_url}/api/materias/{materia_id}",
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise HTTPException(status_code=503, detail="materias-service is unavailable") from exc

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Materia {materia_id} not found")
        if response.status_code >= 400:
            raise HTTPException(status_code=503, detail="Could not validate materia in materias-service")


class PostsClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.posts_service_url).rstrip("/")
        self.timeout = timeout or settings.request_timeout_seconds

    def get_posts_by_tema(self, tema_id: str, authorization: str | None) -> list[dict[str, Any]]:
        headers = {"Authorization": authorization} if authorization else {}
        candidate_paths = [
            f"{self.base_url}/api/posts",
            f"{self.base_url}/posts",
        ]
        params = {"temaId": tema_id}

        last_error_status: int | None = None
        for path in candidate_paths:
            try:
                response = requests.get(path, headers=headers, params=params, timeout=self.timeout)
            except requests.RequestException:
                continue

            if response.status_code == 404:
                last_error_status = 404
                continue

            if response.status_code >= 400:
                raise HTTPException(status_code=503, detail="posts-service returned an unexpected response")

            payload = response.json()
            if isinstance(payload, list):
                return payload
            if isinstance(payload, dict) and isinstance(payload.get("items"), list):
                return payload["items"]
            return []

        if last_error_status == 404:
            raise HTTPException(
                status_code=503,
                detail="posts-service does not expose a tema query endpoint yet",
            )
        raise HTTPException(status_code=503, detail="posts-service is unavailable")
