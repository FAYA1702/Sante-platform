"""Modèles Beanie pour les orientations et assignations médicales.
Tous les champs et commentaires sont rédigés en français.
"""

from enum import Enum
from typing import Optional
from beanie import Document
from datetime import datetime
from pydantic import Field


class ReferralStatus(str, Enum):
    """Statut d'une orientation médicale."""
    pending = "pending"      # En attente de validation
    accepted = "accepted"    # Acceptée par le service
    rejected = "rejected"    # Refusée par le service
    cancelled = "cancelled"  # Annulée


class ReferralSource(str, Enum):
    """Source de l'orientation médicale."""
    ia = "IA"                # Proposée par l'IA
    medecin = "medecin"      # Proposée par un médecin
    admin = "admin"          # Créée par un admin
    patient = "patient"      # Demandée par le patient


class Referral(Document):
    """Document MongoDB représentant une orientation/demande vers un service médical."""

    patient_id: str = Field(..., description="ID du patient orienté")
    proposed_department_id: str = Field(..., description="ID du département proposé")
    status: ReferralStatus = Field(default=ReferralStatus.pending, description="Statut de l'orientation")
    source: ReferralSource = Field(default=ReferralSource.ia, description="Source de l'orientation")
    notes: Optional[str] = Field(None, description="Notes ou justification de l'orientation")
    created_by: Optional[str] = Field(None, description="ID de l'utilisateur créateur")
    processed_by: Optional[str] = Field(None, description="ID du médecin qui a traité la demande")
    processed_at: Optional[datetime] = Field(None, description="Date de traitement")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "referrals"


class AssignmentStatus(str, Enum):
    """Statut d'une assignation patient-médecin."""
    active = "active"        # Assignation active
    ended = "ended"          # Assignation terminée
    suspended = "suspended"  # Assignation suspendue


class Assignment(Document):
    """Document MongoDB représentant une assignation active patient-médecin-département."""

    patient_id: str = Field(..., description="ID du patient assigné")
    department_id: str = Field(..., description="ID du département")
    doctor_id: str = Field(..., description="ID du médecin responsable")
    referral_id: Optional[str] = Field(None, description="ID de l'orientation qui a créé cette assignation")
    status: AssignmentStatus = Field(default=AssignmentStatus.active, description="Statut de l'assignation")
    notes: Optional[str] = Field(None, description="Notes sur l'assignation")
    start_at: datetime = Field(default_factory=datetime.utcnow, description="Date de début")
    end_at: Optional[datetime] = Field(None, description="Date de fin")
    created_by: str = Field(..., description="ID de l'utilisateur qui a créé l'assignation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "assignments"
