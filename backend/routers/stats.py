"""Routeur fournissant les statistiques globales pour le tableau de bord."""

from fastapi import APIRouter, Depends

from backend.dependencies.auth import get_current_user, verifier_roles
from backend.models.device import Device
from backend.models.donnee import Donnee
from backend.models.alerte import Alerte
from backend.models.recommendation import Recommendation
from backend.models.utilisateur import Utilisateur, Role
from backend.schemas.stats import StatsReponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsReponse, dependencies=[Depends(verifier_roles([Role.admin, Role.technicien, Role.medecin, Role.patient]))])
@router.get("/", response_model=StatsReponse, include_in_schema=False)
async def obtenir_stats() -> StatsReponse:
    """Retourne de simples métriques de comptage pour les collections principales."""
    return StatsReponse(
        total_appareils=await Device.count(),
        total_donnees=await Donnee.count(),
        total_alertes=await Alerte.count(),
        total_recommandations=await Recommendation.count(),
        total_utilisateurs=await Utilisateur.count(),
    )
