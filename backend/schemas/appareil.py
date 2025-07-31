"""Schémas Pydantic relatifs aux appareils connectés."""

from pydantic import BaseModel, Field
from typing import Optional

class AppareilBase(BaseModel):
    type: str = Field(..., description="Type d'appareil, ex: 'oxymètre' ou 'bracelet' ")
    numero_serie: str = Field(..., description="Numéro de série unique de l'appareil")


class AppareilCreation(AppareilBase):
    user_id: str = Field(..., description="ID du patient propriétaire")
    """Schéma utilisé lors de l'enregistrement d'un nouvel appareil."""


class AppareilEnDB(AppareilBase):
    """Représentation d'un appareil tel que stocké en base de données."""

    id: str = Field(..., description="Identifiant unique (UUID)")
    user_id: Optional[str] = Field(None, description="ID du patient propriétaire (optionnel pour compatibilité avec anciens appareils)")
    patient_username: Optional[str] = Field(None, description="Nom d'utilisateur du patient (optionnel)")

    model_config = {
        "from_attributes": True
    }
