"""Schémas Pydantic pour les recommandations générées par la plateforme."""

from datetime import datetime
from pydantic import BaseModel, Field


class RecommandationBase(BaseModel):
    titre: str = Field(..., description="Titre de la recommandation")
    description: str = Field(..., description="Description détaillée de la recommandation")
    date: datetime = Field(default_factory=datetime.utcnow, description="Date de création")


class RecommandationCreation(RecommandationBase):
    """Création d'une nouvelle recommandation."""
    priorite: str = Field(default="normale", description="Priorité de la recommandation (faible, normale, élevée)")


class RecommandationEnDB(RecommandationBase):
    user_id: str = Field(..., description="ID du patient concerné")
    id: str = Field(..., description="Identifiant unique de la recommandation (UUID)")

    model_config = {
        "from_attributes": True
    }
