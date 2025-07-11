"""Routeur pour la consultation des alertes."""

from typing import List

from fastapi import APIRouter, Depends

from backend.dependencies.auth import get_current_user


from backend.models.alerte import Alerte
from backend.schemas.alerte import AlerteEnDB

router = APIRouter(dependencies=[Depends(get_current_user)])




@router.get("/alerts", response_model=List[AlerteEnDB])
async def lister_alertes():
    """Liste toutes les alertes de la plateforme (Beanie)."""
    alertes_docs = await Alerte.find_all().to_list()
    return [AlerteEnDB(id=str(a.id), message=a.message, niveau=a.niveau, date=a.date) for a in alertes_docs]
