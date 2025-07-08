"""Modèle Beanie pour les recommandations (collection 'recommandations')."""

from datetime import datetime
from beanie import Document
from pydantic import Field


class Recommandation(Document):
    """Document représentant une recommandation générée pour l'utilisateur."""

    contenu: str = Field(..., description="Contenu de la recommandation")
    date: datetime = Field(default_factory=datetime.utcnow, description="Date de création")

    class Settings:
        name = "recommandations"
