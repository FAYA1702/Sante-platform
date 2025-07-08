"""Routeur d'authentification.
Contient les points d'entrée pour l'inscription et la connexion des utilisateurs.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr

from schemas.utilisateur import UtilisateurInscription, Token

router = APIRouter()

@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
async def inscription(utilisateur: UtilisateurInscription):
    """Inscription d'un nouvel utilisateur.

    Pour l'instant, cette fonction est un stub qui renvoie un identifiant factice.
    L'intégration avec MongoDB sera ajoutée ultérieurement.
    """
    # TODO: sauvegarder l'utilisateur dans la base de données MongoDB
    return {"id": "uuid-généré", "email": utilisateur.email}


@router.post("/login", response_model=Token)
async def connexion(email: EmailStr, mot_de_passe: str):
    """Connexion d'un utilisateur existant.

    À ce stade, la vérification des identifiants est simulée.
    """
    # TODO: vérifier les identifiants dans la base de données et générer un JWT
    if email != "demo@example.com" or mot_de_passe != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")

    return Token(access_token="jeton-jwt-factice", token_type="bearer")
