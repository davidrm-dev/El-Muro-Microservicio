from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.collection import Collection

from app.core.config import get_settings
from app.core.database import mongo_manager


class TemaRepository(ABC):
    @abstractmethod
    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def list(self, *, materia_id: int | None = None, include_inactive: bool = False) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, tema_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def update(self, tema_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def disable(self, tema_id: str) -> dict[str, Any] | None:
        raise NotImplementedError


class MongoTemaRepository(TemaRepository):
    def __init__(self, collection: Collection | None = None) -> None:
        if collection is None:
            settings = get_settings()
            collection = mongo_manager.get_collection(settings.temas_collection)
        self.collection = collection

    def _serialize(self, document: dict[str, Any] | None) -> dict[str, Any] | None:
        if document is None:
            return None

        serialized = dict(document)
        serialized["id"] = str(serialized.pop("_id"))
        return serialized

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        document = {
            "nombre": data["nombre"].strip(),
            "descripcion": data.get("descripcion"),
            "materia_id": data["materia_id"],
            "esta_activo": True,
            "created_at": now,
            "updated_at": now,
        }
        result = self.collection.insert_one(document)
        return self.get_by_id(str(result.inserted_id))  # type: ignore[return-value]

    def list(self, *, materia_id: int | None = None, include_inactive: bool = False) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if materia_id is not None:
            query["materia_id"] = materia_id
        if not include_inactive:
            query["esta_activo"] = True

        documents = self.collection.find(query).sort("nombre", 1)
        return [self._serialize(document) for document in documents if self._serialize(document) is not None]

    def get_by_id(self, tema_id: str) -> dict[str, Any] | None:
        try:
            object_id = ObjectId(tema_id)
        except Exception:
            return None
        document = self.collection.find_one({"_id": object_id})
        return self._serialize(document)

    def update(self, tema_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        try:
            object_id = ObjectId(tema_id)
        except Exception:
            return None

        changes = {key: value for key, value in data.items() if value is not None}
        if not changes:
            document = self.collection.find_one({"_id": object_id})
            return self._serialize(document)

        if "nombre" in changes:
            changes["nombre"] = changes["nombre"].strip()
        changes["updated_at"] = datetime.now(timezone.utc)
        self.collection.update_one({"_id": object_id}, {"$set": changes})
        document = self.collection.find_one({"_id": object_id})
        return self._serialize(document)

    def disable(self, tema_id: str) -> dict[str, Any] | None:
        return self.update(tema_id, {"esta_activo": False})


class InMemoryTemaRepository(TemaRepository):
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}
        self._sequence = 1

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        tema_id = str(self._sequence)
        self._sequence += 1
        tema = {
            "id": tema_id,
            "nombre": data["nombre"].strip(),
            "descripcion": data.get("descripcion"),
            "materia_id": data["materia_id"],
            "esta_activo": True,
            "created_at": now,
            "updated_at": now,
        }
        self._items[tema_id] = tema
        return deepcopy(tema)

    def list(self, *, materia_id: int | None = None, include_inactive: bool = False) -> list[dict[str, Any]]:
        items = list(self._items.values())
        if materia_id is not None:
            items = [item for item in items if item["materia_id"] == materia_id]
        if not include_inactive:
            items = [item for item in items if item["esta_activo"]]
        return [deepcopy(item) for item in sorted(items, key=lambda item: item["nombre"].lower())]

    def get_by_id(self, tema_id: str) -> dict[str, Any] | None:
        tema = self._items.get(tema_id)
        return deepcopy(tema) if tema else None

    def update(self, tema_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        tema = self._items.get(tema_id)
        if tema is None:
            return None
        for key, value in data.items():
            if value is not None:
                tema[key] = value.strip() if key == "nombre" and isinstance(value, str) else value
        tema["updated_at"] = datetime.now(timezone.utc)
        return deepcopy(tema)

    def disable(self, tema_id: str) -> dict[str, Any] | None:
        return self.update(tema_id, {"esta_activo": False})
