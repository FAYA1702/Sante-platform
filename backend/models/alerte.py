"""Modèle Beanie pour les alertes générées (collection 'alertes')."""

from datetime import datetime
from beanie import Document
from pydantic import Field


class Alerte(Document):
    message: str = Field(..., description="Message d'alerte")
    niveau: str = Field(..., description="Niveau de criticité")
    date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "alertes"
