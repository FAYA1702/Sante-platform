"""Modèle Beanie pour la collection des utilisateurs.
Tous les champs et commentaires sont rédigés en français.
"""

from enum import Enum
from typing import Optional

from beanie import Document, Indexed
from pydantic import EmailStr, Field


class Role(str, Enum):
    patient = "patient"
    medecin = "medecin"
    admin = "admin"


class Utilisateur(Document):
    """Document MongoDB représentant un utilisateur de la plateforme."""

    email: Indexed(EmailStr, unique=True)  # type: ignore
    username: Indexed(str, unique=True)  # type: ignore
    mot_de_passe_hache: str = Field(..., min_length=60)
    role: Role = Role.patient

    class Settings:
        name = "utilisateurs"
