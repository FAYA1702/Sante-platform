"""Routeur pour la consultation des recommandations."""

from typing import List

from fastapi import APIRouter


from backend.models.recommandation import Recommandation
from backend.schemas.recommandation import RecommandationEnDB

router = APIRouter()




@router.get("/recommendations", response_model=List[RecommandationEnDB])
async def lister_recommandations():
    """Liste toutes les recommandations disponibles (Beanie)."""
    recos_docs = await Recommandation.find_all().to_list()
    return [RecommandationEnDB(id=str(r.id), contenu=r.contenu, date=r.date) for r in recos_docs]
