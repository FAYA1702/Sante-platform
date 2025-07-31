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


class Utilisateur(Document):
    """Document MongoDB représentant un utilisateur de la plateforme."""

    email: Indexed(EmailStr, unique=True)  # type: ignore
    username: Indexed(str, unique=True)  # type: ignore
    mot_de_passe_hache: str = Field(..., min_length=60)
    role: Role = Role.patient
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    class Settings:
        name = "utilisateurs"
