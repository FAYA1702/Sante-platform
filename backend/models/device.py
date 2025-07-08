"""Modèle Beanie représentant un appareil connecté (collection 'appareils')."""

from beanie import Document
from pydantic import Field


class Device(Document):
    """Modèle d'appareil pour MongoDB avec Beanie."""

    type: str = Field(..., description="Type d'appareil, ex: 'oxymètre'")
    numero_serie: str = Field(..., description="Numéro de série unique")

    class Settings:
        name = "appareils"  # Nom de la collection MongoDB
