"""Schémas Pydantic pour les alertes générées par la plateforme."""

from datetime import datetime
from pydantic import BaseModel, Field


class AlerteBase(BaseModel):
    message: str = Field(..., description="Contenu de l'alerte")
    niveau: str = Field(..., description="Niveau de gravité, ex: 'faible', 'moyen', 'élevé'")
    date: datetime = Field(..., description="Date de génération de l'alerte")


class AlerteCreation(AlerteBase):
    """Création d'une nouvelle alerte (généralement automatique)."""


class AlerteEnDB(AlerteBase):
    id: str = Field(..., description="Identifiant unique de l'alerte (UUID)")

    model_config = {
        "from_attributes": True
    }
