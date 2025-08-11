"""Schémas Pydantic relatifs aux appareils connectés."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AppareilBase(BaseModel):
    type: str = Field(..., description="Type d'appareil, ex: 'oxymetre', 'tensiometre', 'ecg'")
    numero_serie: str = Field(..., description="Numéro de série unique de l'appareil")


class AppareilCreation(AppareilBase):
    user_id: str = Field(..., description="ID du patient propriétaire")
    """Schéma utilisé lors de l'enregistrement d'un nouvel appareil."""


class AppareilEnDB(AppareilBase):
    """Représentation d'un appareil tel que stocké en base de données."""

    id: str = Field(..., description="Identifiant unique (UUID)")
    user_id: Optional[str] = Field(None, description="ID du patient propriétaire (optionnel pour compatibilité avec anciens appareils)")
    patient_username: Optional[str] = Field(None, description="Nom d'utilisateur du patient (optionnel)")
    
    # Champs étendus pour affichage complet
    nom: Optional[str] = Field(None, description="Nom descriptif de l'appareil")
    modele: Optional[str] = Field(None, description="Modèle de l'appareil")
    statut: Optional[str] = Field(None, description="Statut de l'appareil (actif, inactif, maintenance)")
    
    # Dates optionnelles
    date_installation: Optional[datetime] = Field(None, description="Date d'installation")
    derniere_maintenance: Optional[datetime] = Field(None, description="Date de dernière maintenance")
    
    # Champs d'audit
    created_at: Optional[datetime] = Field(None, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")
    is_active: Optional[bool] = Field(None, description="Appareil actif")

    model_config = {
        "from_attributes": True
    }
