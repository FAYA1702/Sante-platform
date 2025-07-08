"""Schémas Pydantic pour les recommandations générées par la plateforme."""

from datetime import datetime
from pydantic import BaseModel, Field


class RecommandationBase(BaseModel):
    contenu: str = Field(..., description="Contenu de la recommandation")
    date: datetime = Field(..., description="Date de création")


class RecommandationCreation(RecommandationBase):
    """Création d'une nouvelle recommandation."""


class RecommandationEnDB(RecommandationBase):
    id: str = Field(..., description="Identifiant unique de la recommandation (UUID)")

    model_config = {
        "from_attributes": True
    }
