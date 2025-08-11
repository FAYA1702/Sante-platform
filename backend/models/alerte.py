"""Modèle Beanie pour les alertes générées (collection 'alertes')."""

from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field


class Alerte(Document):
    user_id: str = Field(..., description="ID du patient concerné par l'alerte")
    message: str = Field(..., description="Message d'alerte")
    niveau: str = Field(..., description="Niveau de criticité")
    date: datetime = Field(default_factory=datetime.utcnow)
    # Filtrage par rôle médical
    priorite_medicale: str = Field(default="normale", description="Priorité: critique, elevee, normale, faible")
    visible_patient: bool = Field(default=True, description="Visible par le patient (filtrage médical)")
    # Statut de consultation
    statut: str = Field(default="nouvelle", description="Statut: nouvelle, vue, archivee")
    vue_par: str = Field(default="", description="ID du médecin/patient qui a vu l'alerte")
    date_vue: Optional[datetime] = Field(default=None, description="Date de consultation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    class Settings:
        name = "alertes"
