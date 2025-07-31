from datetime import datetime
from beanie import Document
from pydantic import Field

class Recommandation(Document):
    """Document représentant une recommandation générée pour l'utilisateur (identique au backend principal)."""
    user_id: str = Field(..., description="ID de l'utilisateur concerné")
    contenu: str = Field(..., description="Contenu de la recommandation")
    date: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    class Settings:
        name = "recommandations"
