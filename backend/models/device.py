"""Modèle Beanie représentant un appareil connecté (collection 'appareils')."""

from beanie import Document
from datetime import datetime
from pydantic import Field
from typing import Optional


class Device(Document):
    """Modèle d'appareil pour MongoDB avec Beanie."""

    # Champs obligatoires
    type: str = Field(..., description="Type d'appareil, ex: 'oxymetre', 'tensiometre', 'ecg'")
    numero_serie: str = Field(..., description="Numéro de série unique")
    user_id: str = Field(..., description="ID du patient propriétaire de l'appareil (RGPD)")
    
    # Champs optionnels pour rétrocompatibilité
    nom: Optional[str] = Field(None, description="Nom descriptif de l'appareil")
    modele: Optional[str] = Field(None, description="Modèle de l'appareil")
    statut: str = Field(default="actif", description="Statut de l'appareil (actif, inactif, maintenance)")
    
    # Dates optionnelles
    date_installation: Optional[datetime] = Field(None, description="Date d'installation de l'appareil")
    derniere_maintenance: Optional[datetime] = Field(None, description="Date de la dernière maintenance")
    
    # Champs d'audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    class Settings:
        name = "appareils"  # Nom de la collection MongoDB
