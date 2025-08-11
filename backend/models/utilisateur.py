"""Modèle Beanie pour la collection des utilisateurs.
Tous les champs et commentaires sont rédigés en français.
"""

from enum import Enum
from typing import Optional

from beanie import Document, Indexed
from datetime import datetime
from pydantic import EmailStr, Field


class Role(str, Enum):
    patient = "patient"
    medecin = "medecin"
    admin = "admin"
    technicien = "technicien"


class StatutUtilisateur(str, Enum):
    """Statut de validation pour les utilisateurs (surtout médecins)."""
    en_attente = "en_attente"
    actif = "actif"
    suspendu = "suspendu"


class Utilisateur(Document):
    """Document MongoDB représentant un utilisateur de la plateforme."""

    email: Indexed(EmailStr, unique=True)  # type: ignore
    username: Indexed(str, unique=True)  # type: ignore
    mot_de_passe_hache: str = Field(..., min_length=60)
    role: Role = Role.patient
    # Statut de validation (pour médecins principalement)
    statut: StatutUtilisateur = Field(default=StatutUtilisateur.actif, description="Statut de validation de l'utilisateur")
    # Associations médecin-patient
    medecin_ids: list[str] = Field(default=[], description="IDs des médecins assignés (pour patients)")
    patient_ids: list[str] = Field(default=[], description="IDs des patients assignés (pour médecins)")
    # Départements/Services (NOUVEAUX CHAMPS - rétrocompatibles)
    department_id: Optional[str] = Field(None, description="ID du département/service (requis pour médecins)")
    current_assignment_id: Optional[str] = Field(None, description="ID de l'assignation active (pour patients)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    class Settings:
        name = "utilisateurs"
