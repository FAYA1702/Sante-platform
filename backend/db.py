"""Configuration et utilitaires pour la connexion à MongoDB.

Utilise Motor (driver asynchrone) afin de fournir l'instance client
partagée dans toute l'application FastAPI.
"""

import os
from functools import lru_cache

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement depuis backend/.env s'il existe
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sante_db")


@lru_cache()
def get_client() -> AsyncIOMotorClient:
    """Retourne une instance singleton d'AsyncIOMotorClient."""

    return AsyncIOMotorClient(MONGO_URI)


def get_database() -> AsyncIOMotorDatabase:  # type: ignore[return-type]
    """Fournit la base de données MongoDB à utiliser dans l'application."""

    return get_client()[MONGO_DB_NAME]
