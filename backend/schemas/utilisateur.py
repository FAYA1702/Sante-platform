"""Schémas Pydantic relatifs aux utilisateurs et à l'authentification."""

from pydantic import BaseModel, EmailStr, Field

class UtilisateurCreation(BaseModel):
    """Données requises pour l'inscription d'un utilisateur."""

    email: EmailStr = Field(..., description="Adresse email de l'utilisateur")
    username: str = Field(..., min_length=3, description="Nom d'utilisateur unique")
    mot_de_passe: str = Field(..., min_length=6, description="Mot de passe de l'utilisateur")


class UtilisateurLogin(BaseModel):
    identifiant: str = Field(..., description="Email ou nom d'utilisateur")
    mot_de_passe: str = Field(..., description="Mot de passe")


class UtilisateurPublic(BaseModel):
    """Informations publiques d'un utilisateur retournées par l'API."""

    id: str
    email: EmailStr
    username: str
    role: str


class Token(BaseModel):
    """Schéma du jeton JWT retourné après la connexion."""

    access_token: str
    token_type: str = "bearer"
