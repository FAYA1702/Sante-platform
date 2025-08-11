"""Schémas Pydantic pour les départements/services médicaux.
Tous les champs et commentaires sont rédigés en français.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DepartmentBase(BaseModel):
    """Schéma de base pour un département."""
    name: str = Field(..., description="Nom du département")
    code: str = Field(..., description="Code du département")
    description: Optional[str] = Field(None, description="Description du département")
    is_active: bool = Field(default=True, description="Département actif")


class DepartmentCreate(DepartmentBase):
    """Schéma pour la création d'un département."""
    pass


class DepartmentUpdate(BaseModel):
    """Schéma pour la mise à jour d'un département."""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    """Schéma de réponse pour un département."""
    id: str = Field(..., description="ID unique du département")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de dernière modification")

    class Config:
        from_attributes = True
