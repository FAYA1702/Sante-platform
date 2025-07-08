"""Routeur pour la gestion des données de santé."""

from typing import List
from datetime import datetime

from fastapi import APIRouter, Query, status
from models.donnee import Donnee
from schemas.donnee import DonneeCreation, DonneeEnDB

router = APIRouter()




@router.post("/data", response_model=DonneeEnDB, status_code=status.HTTP_201_CREATED)
async def ajouter_donnee(donnee: DonneeCreation):
    """Ajoute une donnée de santé dans MongoDB (Beanie)."""
    doc = Donnee(**donnee.dict())
    await doc.insert()
    return DonneeEnDB(id=str(doc.id), **donnee.dict())


@router.get("/data", response_model=List[DonneeEnDB])
async def lister_donnees(
    from_: datetime | None = Query(None, alias="from", description="Date de début (ISO)", example="2025-07-01T00:00:00Z"),
    to: datetime | None = Query(None, description="Date de fin (ISO)", example="2025-07-07T23:59:59Z"),
):
    """Liste les données de santé filtrées par plage de dates (optionnelle)."""

    filtre: dict = {}
    if from_ or to:
        filtre["date"] = {}
        if from_:
            filtre["date"]["$gte"] = from_
        if to:
            filtre["date"]["$lte"] = to

    donnees = await Donnee.find(filtre).to_list()
    return [DonneeEnDB(id=str(d.id), device_id=d.device_id, frequence_cardiaque=d.frequence_cardiaque,
                       pression_arterielle=d.pression_arterielle, taux_oxygene=d.taux_oxygene, date=d.date) for d in donnees]
