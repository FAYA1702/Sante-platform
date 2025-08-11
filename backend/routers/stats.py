"""Routeur fournissant les statistiques globales pour le tableau de bord."""

from fastapi import APIRouter, Depends

from backend.dependencies.auth import get_current_user, verifier_roles
from backend.models.device import Device
from backend.models.donnee import Donnee
from backend.models.alerte import Alerte
from backend.models.recommandation import Recommandation
from backend.models.utilisateur import Utilisateur, Role
from backend.schemas.stats import StatsReponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsReponse)
@router.get("/", response_model=StatsReponse, include_in_schema=False)
async def obtenir_stats(current_user=Depends(get_current_user)) -> StatsReponse:
    """
    Retourne les métriques de comptage pour le tableau de bord.
    - Vue globale pour l'admin (démo/monitoring) : accès à tout (⚠️ À n'activer qu'en démo/supervision, pas en prod réelle sans justification RGPD !)
    - Vue strictement filtrée pour tous les autres (patient, médecin, technicien)
    """
    if current_user.role == "admin":
        return StatsReponse(
            total_appareils=await Device.find().count(),
            total_donnees=await Donnee.find().count(),
            total_alertes=await Alerte.find().count(),
            total_recommandations=await Recommandation.find().count(),
            total_utilisateurs=await Utilisateur.find().count(),
        )
    user_id = str(current_user.id)
    return StatsReponse(
        total_appareils=await Device.find({"user_id": user_id}).count(),
        total_donnees=await Donnee.find({"user_id": user_id}).count(),
        total_alertes=await Alerte.find({"user_id": user_id}).count(),
        total_recommandations=await Recommandation.find({"user_id": user_id}).count(),
        total_utilisateurs=1,
    )
