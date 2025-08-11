"""Dépendances FastAPI pour l'authentification et le contrôle RBAC.
Toutes les fonctions sont rédigées en français.
"""

from typing import Annotated, List, Optional

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from backend.models.utilisateur import Utilisateur, Role
from backend.settings import DEMO_MODE
from backend.utils.auth import verifier_jwt

# Schéma de sécurité HTTP Bearer (JWT)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(

    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> Utilisateur:
    """Retourne l'utilisateur actuellement authentifié via le JWT dans l'en-tête Authorization.

    Le JWT doit être envoyé sous la forme « Bearer <token> ».
    """

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Jeton manquant")

    token = credentials.credentials
    payload = verifier_jwt(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Jeton invalide ou expiré")

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Jeton invalide")

    user = await Utilisateur.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")

    return user


def roles_sante() -> List[Role]:
    """Retourne la liste des rôles ayant accès aux données santé.

    - Toujours Patient et Médecin.
    - Admin uniquement si DEMO_MODE est actif.
    """
    base = [Role.patient, Role.medecin]
    if DEMO_MODE:
        base.append(Role.admin)
    return base


def verifier_roles(roles_autorises: List[Role]):
    """Génère une dépendance qui valide que l'utilisateur possède l'un des rôles autorisés."""

    async def _verifier(user: Utilisateur = Depends(get_current_user)) -> Utilisateur:
        if user.role not in roles_autorises:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
        return user

    return _verifier


def require_role(role: str):
    """Génère une dépendance qui valide que l'utilisateur possède le rôle spécifié."""
    
    async def _verifier(user: Utilisateur = Depends(get_current_user)) -> Utilisateur:
        if user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Accès refusé. Rôle requis: {role}"
            )
        return user
    
    return _verifier
