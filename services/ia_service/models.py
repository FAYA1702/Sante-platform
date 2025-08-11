from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field

class Recommandation(Document):
    """Document représentant une recommandation générée pour l'utilisateur (identique au backend principal)."""
    user_id: str = Field(..., description="ID de l'utilisateur concerné")
    titre: Optional[str] = Field(default="Recommandation de santé", description="Titre court de la recommandation")
    description: Optional[str] = Field(default="Aucune description disponible", description="Description détaillée de la recommandation")
    date: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    # Ancien champ pour rétrocompatibilité
    contenu: str | None = Field(None, description="Ancien champ de contenu (rétrocompatibilité)")
    
    # Configuration du modèle Pydantic v2
    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }

    class Settings:
        name = "recommandations"
