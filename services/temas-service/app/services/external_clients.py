from __future__ import annotations

from typing import Any

import requests
from fastapi import HTTPException

from app.core.config import get_settings
from app.core.service_discovery import ServiceDiscoveryError, discover_service_url


class MateriasClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        settings = get_settings()
        self.service_name = settings.materias_service_name
        self.base_url = base_url.rstrip("/") if base_url else None
        self.timeout = timeout or settings.request_timeout_seconds

    def _base_url(self) -> str:
        if self.base_url:
            return self.base_url
        try:
            return discover_service_url(self.service_name, timeout=self.timeout)
        except (requests.RequestException, ServiceDiscoveryError) as exc:
            raise HTTPException(status_code=503, detail="Could not resolve materias-service via Eureka") from exc

    def ensure_materia_exists(self, materia_id: int, authorization: str | None) -> None:
        headers = {"Authorization": authorization} if authorization else {}
        try:
            response = requests.get(
                f"{self._base_url()}/api/materias/{materia_id}",
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
        self.service_name = settings.posts_service_name
        self.base_url = base_url.rstrip("/") if base_url else None
        self.timeout = timeout or settings.request_timeout_seconds

    def _base_url(self) -> str:
        if self.base_url:
            return self.base_url
        try:
            return discover_service_url(self.service_name, timeout=self.timeout)
        except (requests.RequestException, ServiceDiscoveryError) as exc:
            raise HTTPException(status_code=503, detail="Could not resolve posts-service via Eureka") from exc

    def get_posts_by_tema(self, tema_id: str, authorization: str | None) -> list[dict[str, Any]]:
        headers = {"Authorization": authorization} if authorization else {}
        candidate_paths = [
            f"{self._base_url()}/api/posts",
            f"{self._base_url()}/posts",
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
