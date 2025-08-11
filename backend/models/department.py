"""Modèle Beanie pour la collection des départements/services médicaux.
Tous les champs et commentaires sont rédigés en français.
"""

from typing import Optional
from beanie import Document, Indexed
from datetime import datetime
from pydantic import Field


class Department(Document):
    """Document MongoDB représentant un département/service médical."""

    name: Indexed(str, unique=True) = Field(..., description="Nom du département (ex: Cardiologie)")  # type: ignore
    code: Indexed(str, unique=True) = Field(..., description="Code du département (ex: CARDIO)")  # type: ignore
    description: Optional[str] = Field(None, description="Description détaillée du département")
    is_active: bool = Field(default=True, description="Département actif ou non")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "departments"
