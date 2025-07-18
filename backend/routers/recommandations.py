"""Routeur pour la consultation des recommandations."""

from typing import List

from fastapi import APIRouter, Depends


from backend.models.recommendation import Recommendation
from backend.schemas.recommandation import RecommandationEnDB, RecommandationCreation

from backend.dependencies.auth import get_current_user, verifier_roles
from backend.models.utilisateur import Role

router = APIRouter(tags=["recommendations"])




@router.post("/recommendations", response_model=RecommandationEnDB, status_code=201,
             dependencies=[Depends(verifier_roles([Role.medecin, Role.admin]))])
async def creer_recommandation(reco: RecommandationCreation, current_user=Depends(get_current_user)):
    """Crée une recommandation pour un patient (utilisable par un médecin ou l’IA)."""
    doc = Recommendation(user_id=reco.user_id if hasattr(reco, 'user_id') else str(current_user.id),
                         titre=reco.titre, description=reco.description, date=reco.date)
    await doc.insert()
    return RecommandationEnDB(id=str(doc.id), user_id=doc.user_id, titre=doc.titre, description=doc.description, date=doc.date)


@router.get("/recommendations", response_model=List[RecommandationEnDB])
async def lister_recommandations(current_user=Depends(get_current_user)):
    """Renvoie les recommandations du patient connecté.
    Si aucune recommandation n'est trouvée, renvoie une liste vide (le frontend affichera des exemples fictifs).
    """
    docs = await Recommendation.find({"user_id": str(current_user.id)}).to_list()
    return [RecommandationEnDB(id=str(d.id), user_id=d.user_id, titre=d.titre, description=d.description, date=d.date) for d in docs]
