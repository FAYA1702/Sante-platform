"""Schémas Pydantic pour les orientations et assignations médicales.
Tous les champs et commentaires sont rédigés en français.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from ..models.referral import ReferralStatus, ReferralSource, AssignmentStatus


class ReferralBase(BaseModel):
    """Schéma de base pour une orientation médicale."""
    patient_id: str = Field(..., description="ID du patient")
    proposed_department_id: str = Field(..., description="ID du département proposé")
    notes: Optional[str] = Field(None, description="Notes sur l'orientation")


class ReferralCreate(ReferralBase):
    """Schéma pour la création d'une orientation."""
    source: ReferralSource = Field(default=ReferralSource.ia, description="Source de l'orientation")
    created_by: Optional[str] = Field(None, description="ID du créateur")


class ReferralUpdate(BaseModel):
    """Schéma pour la mise à jour d'une orientation."""
    status: Optional[ReferralStatus] = None
    notes: Optional[str] = None
    processed_by: Optional[str] = None


class ReferralResponse(ReferralBase):
    """Schéma de réponse pour une orientation."""
    id: str = Field(..., description="ID unique de l'orientation")
    status: ReferralStatus = Field(..., description="Statut de l'orientation")
    source: ReferralSource = Field(..., description="Source de l'orientation")
    created_by: Optional[str] = Field(None, description="ID du créateur")
    processed_by: Optional[str] = Field(None, description="ID du médecin traitant")
    processed_at: Optional[datetime] = Field(None, description="Date de traitement")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de modification")
    # Champs enrichis (optionnels)
    patient_name: Optional[str] = Field(None, description="Nom du patient")
    department_name: Optional[str] = Field(None, description="Nom du département")
    created_by_name: Optional[str] = Field(None, description="Nom du créateur")

    class Config:
        from_attributes = True


class AssignmentBase(BaseModel):
    """Schéma de base pour une assignation."""
    patient_id: str = Field(..., description="ID du patient")
    department_id: str = Field(..., description="ID du département")
    doctor_id: str = Field(..., description="ID du médecin")
    notes: Optional[str] = Field(None, description="Notes sur l'assignation")


class AssignmentCreate(AssignmentBase):
    """Schéma pour la création d'une assignation."""
    referral_id: Optional[str] = Field(None, description="ID de l'orientation source")
    created_by: str = Field(..., description="ID du créateur")


class AssignmentUpdate(BaseModel):
    """Schéma pour la mise à jour d'une assignation."""
    status: Optional[AssignmentStatus] = None
    notes: Optional[str] = None
    end_at: Optional[datetime] = None


class AssignmentResponse(AssignmentBase):
    """Schéma de réponse pour une assignation."""
    id: str = Field(..., description="ID unique de l'assignation")
    referral_id: Optional[str] = Field(None, description="ID de l'orientation source")
    status: AssignmentStatus = Field(..., description="Statut de l'assignation")
    start_at: datetime = Field(..., description="Date de début")
    end_at: Optional[datetime] = Field(None, description="Date de fin")
    created_by: str = Field(..., description="ID du créateur")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de modification")
    # Champs enrichis (optionnels)
    patient_name: Optional[str] = Field(None, description="Nom du patient")
    department_name: Optional[str] = Field(None, description="Nom du département")
    doctor_name: Optional[str] = Field(None, description="Nom du médecin")
    created_by_name: Optional[str] = Field(None, description="Nom du créateur")

    class Config:
        from_attributes = True
