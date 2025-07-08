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

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def inscription(utilisateur: UtilisateurCreation):
    """Inscription d'un nouvel utilisateur (stockage MongoDB, mot de passe haché)."""
    # Vérifier unicité email/username
    if await Utilisateur.find_one({"email": utilisateur.email}):
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")
    if await Utilisateur.find_one({"username": utilisateur.username}):
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà utilisé.")
    # Hashage du mot de passe
    hash_ = hacher_mot_de_passe(utilisateur.mot_de_passe)
    user = Utilisateur(email=utilisateur.email, username=utilisateur.username, mot_de_passe_hache=hash_)
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
