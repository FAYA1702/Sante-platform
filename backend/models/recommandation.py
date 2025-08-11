"""Modèle Beanie pour les recommandations (collection 'recommandations')."""

from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field


class Recommandation(Document):
    """Document représentant une recommandation générée pour l'utilisateur."""

    user_id: str = Field(..., description="ID de l'utilisateur concerné")
    titre: Optional[str] = Field(default="Recommandation de santé", description="Titre court de la recommandation")
    description: Optional[str] = Field(default="Aucune description disponible", description="Description détaillée de la recommandation")
    date: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    # Filtrage par rôle médical
    priorite_medicale: str = Field(default="normale", description="Priorité: critique, elevee, normale, faible")
    visible_patient: bool = Field(default=True, description="Visible par le patient (filtrage médical)")
    validation_medicale: bool = Field(default=False, description="Recommandation validée par un médecin")
    # Statut de consultation
    statut: str = Field(default="nouvelle", description="Statut: nouvelle, vue, archivee")
    vue_par: str = Field(default="", description="ID du médecin/patient qui a vu la recommandation")
    date_vue: Optional[datetime] = Field(default=None, description="Date de consultation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    # Ancien champ pour rétrocompatibilité
    contenu: str | None = Field(None, description="Ancien champ de contenu (rétrocompatibilité)")
    
    # Configuration du modèle Pydantic v2
    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "titre": "Recommandation de santé",
                "description": "Description détaillée de la recommandation",
                "user_id": "507f1f77bcf86cd799439011"
            }
        }
    }

    class Settings:
        name = "recommandations"
