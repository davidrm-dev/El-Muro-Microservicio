from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

from pymongo import MongoClient


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import get_settings


DEFAULT_TEMAS = [
    {
        "nombre": "Matrices",
        "descripcion": "Operaciones basicas, determinantes e introduccion a transformaciones lineales.",
        "materia_id": 1,
    },
    {
        "nombre": "Limites",
        "descripcion": "Conceptos iniciales de limites, continuidad y aproximacion de funciones.",
        "materia_id": 2,
    },
    {
        "nombre": "Programacion Orientada a Objetos",
        "descripcion": "Clases, objetos, encapsulamiento, herencia y polimorfismo.",
        "materia_id": 3,
    },
]


def seed_temas() -> None:
    settings = get_settings()
    client = MongoClient(settings.mongo_uri)
    collection = client[settings.mongo_database][settings.temas_collection]

    inserted = 0
    updated = 0
    now = datetime.now(timezone.utc)

    try:
        for tema in DEFAULT_TEMAS:
            query = {
                "nombre": tema["nombre"],
                "materia_id": tema["materia_id"],
            }
            existing = collection.find_one(query)

            if existing:
                collection.update_one(
                    {"_id": existing["_id"]},
                    {
                        "$set": {
                            "descripcion": tema["descripcion"],
                            "esta_activo": True,
                            "updated_at": now,
                        }
                    },
                )
                updated += 1
                print(f"[updated] {tema['nombre']} (materia_id={tema['materia_id']})")
                continue

            collection.insert_one(
                {
                    **tema,
                    "esta_activo": True,
                    "created_at": now,
                    "updated_at": now,
                }
            )
            inserted += 1
            print(f"[inserted] {tema['nombre']} (materia_id={tema['materia_id']})")
    finally:
        client.close()

    print()
    print("Seed completado")
    print(f"- insertados: {inserted}")
    print(f"- actualizados: {updated}")
    print(f"- base de datos: {settings.mongo_database}")
    print(f"- coleccion: {settings.temas_collection}")


if __name__ == "__main__":
    seed_temas()
