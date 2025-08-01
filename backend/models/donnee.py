"""Modèle Beanie pour les données de santé (collection 'donnees')."""

from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class Donnee(Document):
    """Document représentant une mesure de santé provenant d'un appareil."""

    device_id: str = Field(..., description="Identifiant de l'appareil (UUID)")
    user_id: str = Field(..., description="ID du patient propriétaire de la donnée")  # RGPD : chaque donnée est liée à un patient
    frequence_cardiaque: Optional[float] = Field(None, description="Fréquence cardiaque en bpm")
    pression_arterielle: Optional[str] = Field(None, description="Pression artérielle ex: '120/80'")
    taux_oxygene: Optional[float] = Field(None, description="Taux d'oxygène SpO2 en %")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    date: datetime = Field(default_factory=datetime.utcnow, description="Horodatage de la mesure")

    class Settings:
        name = "donnees"
