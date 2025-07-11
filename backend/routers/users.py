"""Routes liées à la gestion des utilisateurs et des rôles (RBAC)."""

from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId

from backend.dependencies.auth import get_current_user, verifier_roles
from backend.models.utilisateur import Utilisateur, Role
from backend.schemas.utilisateur import UtilisateurPublic
from backend.schemas.role_update import RoleUpdate

router = APIRouter(prefix="/users", tags=["utilisateurs"])


@router.get("/me", response_model=UtilisateurPublic)
async def lire_profil(utilisateur: Utilisateur = Depends(get_current_user)):
    """Renvoie le profil de l'utilisateur connecté."""
    return UtilisateurPublic(
        id=str(utilisateur.id),
        email=utilisateur.email,
        username=utilisateur.username,
        role=utilisateur.role,
    )


@router.patch("/{user_id}/role", response_model=UtilisateurPublic, status_code=status.HTTP_200_OK,
              dependencies=[Depends(verifier_roles([Role.admin]))])
async def changer_role(user_id: PydanticObjectId, payload: RoleUpdate):
    """Permet à un administrateur de changer le rôle d'un utilisateur donné."""
    user = await Utilisateur.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    user.role = payload.role
    await user.save()

    return UtilisateurPublic(
        id=str(user.id),
        email=user.email,
        username=user.username,
        role=user.role,
    )
