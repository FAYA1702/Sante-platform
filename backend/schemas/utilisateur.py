"""Schémas Pydantic relatifs aux utilisateurs et à l'authentification."""

from pydantic import BaseModel, EmailStr, Field

class UtilisateurInscription(BaseModel):
    """Données requises pour l'inscription d'un utilisateur."""

    email: EmailStr = Field(..., description="Adresse email de l'utilisateur")
    mot_de_passe: str = Field(..., min_length=6, description="Mot de passe de l'utilisateur")


class Token(BaseModel):
    """Schéma du jeton JWT retourné après la connexion."""

    access_token: str
    token_type: str = "bearer"
