"""Modèle Recommendation (Beanie).

Représente une recommandation santé générée par l’IA pour un patient.
- user_id : référence du patient concerné
- titre / description : contenu affiché
- date : date ISO de génération
"""
from datetime import datetime
from beanie import Document
from pydantic import Field
from typing import Optional


class Recommendation(Document):
    user_id: str = Field(..., description="ID Mongo de l’utilisateur patient concerné")
    titre: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "recommendations"
