"""Schémas Pydantic pour les données de santé transmises par les appareils."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DonneeBase(BaseModel):
    device_id: str = Field(..., description="Identifiant de l'appareil (UUID)")
    frequence_cardiaque: Optional[float] = Field(None, description="Fréquence cardiaque en bpm")
    pression_arterielle: Optional[str] = Field(None, description="Pression artérielle ex: '120/80'")
    taux_oxygene: Optional[float] = Field(None, description="Taux d'oxygène SpO2 en %")
    date: datetime = Field(..., description="Horodatage de la mesure")


class DonneeCreation(DonneeBase):
    """Schéma utilisé lors de la création d'une donnée de santé."""
    user_id: Optional[str] = Field(None, description="ID du patient propriétaire (rempli côté backend)")


class DonneeEnDB(DonneeBase):
    id: str = Field(..., description="Identifiant unique de la donnée (UUID)")
    patient_nom: str | None = Field(None, description="Nom complet du patient")
    device_nom: str | None = Field(None, description="Nom de l'appareil (type + série)")
    user_id: str = Field(..., description="ID du patient propriétaire de la donnée")

    model_config = {
        "from_attributes": True
    }
