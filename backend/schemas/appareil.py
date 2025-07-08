"""Schémas Pydantic relatifs aux appareils connectés."""

from pydantic import BaseModel, Field
from typing import Optional

class AppareilBase(BaseModel):
    type: str = Field(..., description="Type d'appareil, ex: 'oxymètre' ou 'bracelet' ")
    numero_serie: str = Field(..., description="Numéro de série unique de l'appareil")


class AppareilCreation(AppareilBase):
    """Schéma utilisé lors de l'enregistrement d'un nouvel appareil."""


class AppareilEnDB(AppareilBase):
    """Représentation d'un appareil tel que stocké en base de données."""

    id: str = Field(..., description="Identifiant unique (UUID)")

    model_config = {
        "from_attributes": True
    }
