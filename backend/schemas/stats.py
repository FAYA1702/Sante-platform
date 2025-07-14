"""Schéma de réponse pour les statistiques globales du tableau de bord."""

from pydantic import BaseModel, Field


class StatsReponse(BaseModel):
    """Nombre d'objets stockés dans chaque collection."""

    total_appareils: int = Field(..., description="Nombre total d'appareils connectés")
    total_donnees: int = Field(..., description="Nombre total de documents DonneeSante")
    total_alertes: int = Field(..., description="Nombre total d'alertes IA")
    total_recommandations: int = Field(..., description="Nombre total de recommandations")
    total_utilisateurs: int = Field(..., description="Nombre total d'utilisateurs enregistrés")

    class Config:
        orm_mode = True
        from_attributes = True
