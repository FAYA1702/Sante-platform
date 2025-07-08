"""Routeur démonstration pour RBAC.
Contient des routes protégées selon le rôle de l'utilisateur.
"""

from fastapi import APIRouter, Depends, status

from backend.dependencies.auth import verifier_roles, get_current_user
from backend.models.utilisateur import Role, Utilisateur

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/profile")
async def mon_profil(user: Utilisateur = Depends(get_current_user)):
    """Renvoie les informations du profil courant, accessible à tout utilisateur authentifié."""
    return {"username": user.username, "role": user.role}


@router.get("/admin", status_code=status.HTTP_200_OK)
async def admin_only(user: Utilisateur = Depends(verifier_roles([Role.admin]))):
    """Route réservée aux administrateurs."""
    return {"message": "Bienvenue, administrateur."}
