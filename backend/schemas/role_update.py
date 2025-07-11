"""Schéma pour la mise à jour du rôle d'un utilisateur."""

from pydantic import BaseModel, Field
from backend.models.utilisateur import Role


class RoleUpdate(BaseModel):
    """Payload envoyé par un administrateur pour changer le rôle d'un utilisateur."""

    role: Role = Field(..., description="Nouveau rôle attribué à l'utilisateur")
