"""Dépendances FastAPI pour l'authentification et le contrôle RBAC.
Toutes les fonctions sont rédigées en français.
"""

from typing import Annotated, List, Optional

from fastapi import Depends, HTTPException, status, Header
from jose import JWTError

from backend.models.utilisateur import Utilisateur, Role
from backend.utils.auth import verifier_jwt


async def get_current_user(authorization: Annotated[Optional[str], Header(alias="Authorization")] = None) -> Utilisateur:
    """Retourne l'utilisateur actuellement authentifié via le JWT dans l'en-tête Authorization.

    Le JWT doit être envoyé sous la forme « Bearer <token> ».
    """

    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Jeton manquant")

    token = authorization.split()[1]
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


def verifier_roles(roles_autorises: List[Role]):
    """Génère une dépendance qui valide que l'utilisateur possède l'un des rôles autorisés."""

    async def _verifier(user: Utilisateur = Depends(get_current_user)) -> Utilisateur:
        if user.role not in roles_autorises:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
        return user

    return _verifier
