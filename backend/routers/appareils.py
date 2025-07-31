"""Routeur pour la gestion des appareils connectés."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from backend.dependencies.auth import get_current_user, verifier_roles
from backend.models.utilisateur import Role

from backend.schemas.appareil import AppareilCreation, AppareilEnDB
from backend.models.device import Device
from backend.models.utilisateur import Utilisateur
from beanie import PydanticObjectId


router = APIRouter()

COLLECTION = "appareils"


@router.get("/devices", response_model=List[AppareilEnDB],
              dependencies=[Depends(verifier_roles([Role.admin, Role.technicien]))])
async def lister_appareils():
    """
    Retourne la liste de tous les appareils enregistrés.
    L'accès est restreint aux utilisateurs avec le rôle d'administrateur ou de technicien.
    """
    appareils = await Device.find_all().to_list()

    # Récupérer en une requête tous les utilisateurs concernés
    user_ids = list({a.user_id for a in appareils if a.user_id})
    utilisateurs = await Utilisateur.find({"_id": {"$in": [PydanticObjectId(uid) for uid in user_ids]}}).to_list() if user_ids else []
    username_map = {str(u.id): u.username for u in utilisateurs}

    return [
        AppareilEnDB(
            id=str(a.id),
            type=a.type,
            numero_serie=a.numero_serie,
            user_id=a.user_id,
            patient_username=username_map.get(a.user_id)
        )
        for a in appareils
    ]


# -----------------------------------------------------------------------------
# Endpoint patient : liste de ses propres appareils
# -----------------------------------------------------------------------------
@router.get("/my/devices", response_model=List[AppareilEnDB],
            dependencies=[Depends(verifier_roles([Role.patient]))])
async def lister_appareils_patient(current_user=Depends(get_current_user)):
    """Retourne les appareils appartenant au patient connecté."""
    appareils = await Device.find({"user_id": str(current_user.id)}).to_list()
    return [
        AppareilEnDB(
            id=str(a.id),
            type=a.type,
            numero_serie=a.numero_serie,
            user_id=a.user_id,
            patient_username=current_user.username
        ) for a in appareils
    ]


@router.post("/devices", response_model=AppareilEnDB, status_code=status.HTTP_201_CREATED,
              dependencies=[Depends(verifier_roles([Role.admin, Role.technicien]))])
async def ajouter_appareil(appareil: AppareilCreation):
    """Enregistre un nouvel appareil dans la base."""
    doc = Device(**appareil.model_dump())
    await doc.insert()

    username = None
    if doc.user_id:
        user = await Utilisateur.get(PydanticObjectId(doc.user_id))
        username = user.username if user else None

    return AppareilEnDB(
        id=str(doc.id),
        type=doc.type,
        numero_serie=doc.numero_serie,
        user_id=doc.user_id,
        patient_username=username,
    )
