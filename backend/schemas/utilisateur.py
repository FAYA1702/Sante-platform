"""Schémas Pydantic relatifs aux utilisateurs et à l'authentification."""

from pydantic import BaseModel, EmailStr, Field

class UtilisateurCreation(BaseModel):
    """Données requises pour l'inscription d'un utilisateur. Le rôle ne peut être que 'patient' ou 'medecin' lors d'une inscription publique."""

    email: EmailStr = Field(..., description="Adresse email de l'utilisateur")
    username: str = Field(..., min_length=3, pattern=r'^[a-zA-Z0-9_.-]+$', description="Nom d'utilisateur unique (3 caractères min, sans espace)")
    mot_de_passe: str = Field(..., min_length=6, description="Mot de passe de l'utilisateur")
    role: str = Field('patient', description="Rôle de l'utilisateur (patient ou medecin seulement)")
    department_id: str | None = Field(None, description="ID du département choisi (requis pour patients)")


class UtilisateurLogin(BaseModel):
    identifiant: str = Field(..., description="Email ou nom d'utilisateur")
    mot_de_passe: str = Field(..., description="Mot de passe")


class UtilisateurPublic(BaseModel):
    """Informations publiques d'un utilisateur retournées par l'API."""

    id: str
    email: EmailStr
    username: str
    role: str
    # Champs département (optionnels pour rétrocompatibilité)
    department_id: str | None = None
    department_name: str | None = None
    department_code: str | None = None


class UtilisateurAdminCreate(BaseModel):
    """Schéma utilisé par un administrateur pour créer un utilisateur.
    Contrairement à l'inscription publique, tous les rôles sont autorisés."""

    email: EmailStr
    username: str = Field(..., min_length=3, pattern=r'^[a-zA-Z0-9_.-]+$')
    mot_de_passe: str = Field(..., min_length=6)
    role: str = Field(..., description="Rôle attribué à la création")
    department_id: str | None = Field(None, description="ID du département (requis pour médecins)")


class UtilisateurUpdate(BaseModel):
    """Schéma de mise à jour partielle d'un utilisateur (admin)."""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, pattern=r'^[a-zA-Z0-9_.-]+$')
    role: str | None = None
    department_id: str | None = Field(None, description="ID du département")


class Token(BaseModel):
    """Schéma du jeton JWT retourné après la connexion."""

    access_token: str
    token_type: str = "bearer"
