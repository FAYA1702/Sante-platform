"""Routeur d'authentification.
Contient les points d'entrée pour l'inscription et la connexion des utilisateurs.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from backend.models.utilisateur import Utilisateur, Role
from backend.schemas.utilisateur import UtilisateurCreation, UtilisateurLogin, Token
from backend.utils.auth import hacher_mot_de_passe, verifier_mot_de_passe, creer_jwt
from beanie import PydanticObjectId
from pydantic import EmailStr



router = APIRouter()

#
# Route spéciale pour la création d’admin/technicien (réservée à l’admin, non documentée dans l’OpenAPI)
# Usage : POST /auth/register-admin (body = UtilisateurCreation avec role=admin ou technicien)
# ⚠️ Ne jamais exposer cette route en production sans contrôle strict !
from fastapi import Security
from backend.dependencies.auth import verifier_roles, get_current_user

@router.post("/register-admin", response_model=Token, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def inscription_admin(utilisateur: UtilisateurCreation, user=Security(verifier_roles([Role.admin]))):
    """Permet à un administrateur de créer un compte admin ou technicien."""
    if utilisateur.role not in ("admin", "technicien"):
        raise HTTPException(status_code=400, detail="Le rôle doit être 'admin' ou 'technicien'.")
    if await Utilisateur.find_one({"email": utilisateur.email}):
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")
    if await Utilisateur.find_one({"username": utilisateur.username}):
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà utilisé.")
    hash_ = hacher_mot_de_passe(utilisateur.mot_de_passe)
    user_obj = Utilisateur(email=utilisateur.email, username=utilisateur.username, mot_de_passe_hache=hash_, role=utilisateur.role)
    await user_obj.insert()
    token = creer_jwt({"sub": str(user_obj.id), "role": user_obj.role})
    return Token(access_token=token, token_type="bearer")

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def inscription(utilisateur: UtilisateurCreation):
    """Inscription d'un nouvel utilisateur (stockage MongoDB, mot de passe haché).
    Seuls les rôles 'patient' ou 'medecin' sont acceptés à l'inscription publique.
    """
    # Vérifier unicité email/username
    if await Utilisateur.find_one({"email": utilisateur.email}):
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")
    if await Utilisateur.find_one({"username": utilisateur.username}):
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà utilisé.")
    # Sécurité : n'accepter que patient ou medecin
    if utilisateur.role not in ("patient", "medecin"):
        raise HTTPException(status_code=400, detail="Le rôle doit être 'patient' ou 'medecin'.")
    # Hashage du mot de passe
    hash_ = hacher_mot_de_passe(utilisateur.mot_de_passe)
    user = Utilisateur(email=utilisateur.email, username=utilisateur.username, mot_de_passe_hache=hash_, role=utilisateur.role)
    await user.insert()
    token = creer_jwt({"sub": str(user.id), "role": user.role})
    return Token(access_token=token, token_type="bearer")


@router.post("/login", response_model=Token)
async def connexion(credentials: UtilisateurLogin):
    """Connexion d'un utilisateur (vérification hash, JWT)."""
    # Recherche par email OU username
    user = await Utilisateur.find_one({"$or": [
        {"email": credentials.identifiant},
        {"username": credentials.identifiant}
    ]})
    if not user or not verifier_mot_de_passe(credentials.mot_de_passe, user.mot_de_passe_hache):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")
    token = creer_jwt({"sub": str(user.id), "role": user.role})
    return Token(access_token=token, token_type="bearer")
