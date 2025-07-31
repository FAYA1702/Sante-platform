"""Routeur pour la gestion des données de santé."""

from typing import List
from datetime import datetime

from fastapi import APIRouter, Query, status, Depends

from backend.dependencies.auth import get_current_user, verifier_roles, roles_sante
from backend.models.utilisateur import Role, Utilisateur
from backend.models.donnee import Donnee
from backend.models.device import Device
from backend.event_bus import publish as publish_event
from backend.schemas.donnee import DonneeCreation, DonneeEnDB

router = APIRouter()

@router.get("/data/test")
async def test_data_endpoint():
    """Endpoint de test pour diagnostiquer les problèmes de données."""
    try:
        donnees = await Donnee.find().limit(3).to_list()
        return {
            "status": "ok",
            "count": len(donnees),
            "sample": [d.dict() for d in donnees[:2]] if donnees else []
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}




@router.post("/data", response_model=DonneeEnDB, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(verifier_roles([Role.patient, Role.medecin]))])
async def ajouter_donnee(donnee: DonneeCreation, current_user=Depends(get_current_user)):
    """
    Ajoute une donnée de santé dans MongoDB (Beanie).
    Le champ user_id est automatiquement renseigné avec l’ID du patient connecté (RGPD).
    """
    donnee_data = donnee.model_dump(exclude={"user_id"})
    # Insertion en BDD avec l’ID du patient courant
    doc = Donnee(**donnee_data, user_id=str(current_user.id))
    await doc.insert()

    # Publication d'un événement pour déclencher l'analyse IA
    await publish_event(
        "nouvelle_donnee",
        {
            "donnee_id": str(doc.id),
            "device_id": doc.device_id,
        },
    )

    # Retourne la donnée insérée sans passer deux fois user_id
    return DonneeEnDB(id=str(doc.id), user_id=str(current_user.id), **donnee_data)


#
# Accès strictement réservé aux patients et médecins (conforme RGPD, secret médical)
# Pour la démo, tu peux décommenter la ligne suivante pour autoriser l’admin :
# dependencies=[Depends(verifier_roles(roles_sante()))]
# ⚠️ Ne jamais activer cette option en production sans justification légale !
# Accès strictement réservé aux patients et médecins (conforme RGPD, secret médical)
# Pour la démo, tu peux décommenter la ligne suivante pour autoriser l’admin :
# dependencies=[Depends(verifier_roles(roles_sante()))]
# ⚠️ Ne jamais activer cette option en production sans justification légale !
@router.get("/data", response_model=List[DonneeEnDB],
            dependencies=[Depends(verifier_roles(roles_sante()))])
async def lister_donnees(
    from_: datetime | None = Query(
        None,
        alias="from",
        description="Date de début (ISO)",
        examples={"2025-07-01T00:00:00Z": {"summary": "Début"}},
    ),
    to: datetime | None = Query(
        None,
        description="Date de fin (ISO)",
        examples={"2025-07-07T23:59:59Z": {"summary": "Fin"}},
    ),
    current_user=Depends(get_current_user)
):
    """
    Liste les données de santé filtrées par plage de dates et par utilisateur (RGPD).
    - Patient : ne voit que ses propres données.
    - Médecin : voit toutes les données (démo, à restreindre à ses patients en prod).
    - Admin : accès autorisé uniquement pour la démo/documentation (jamais en prod RGPD).
    """
    filtre: dict = {}
    if from_ or to:
        filtre["date"] = {}
        if from_:
            filtre["date"]["$gte"] = from_
        if to:
            filtre["date"]["$lte"] = to
    # Filtrage RGPD selon le rôle
    if current_user.role == Role.patient:
        filtre["user_id"] = str(current_user.id)
    # Médecin : accès à toutes les données (démo). Pour restreindre, filtrer sur ses patients.
    # Admin : accès démo/documenté (jamais en prod RGPD)
    donnees = await Donnee.find(filtre).to_list()
    # Récupère les noms patients et appareils en une seule requête
    user_ids = list({d.user_id for d in donnees})
    device_ids = list({d.device_id for d in donnees if d.device_id})
    from beanie import PydanticObjectId
    from bson.errors import InvalidId
    
    # Filtre les ObjectIds valides pour les utilisateurs
    valid_user_ids = []
    for uid in user_ids:
        try:
            PydanticObjectId(uid)
            valid_user_ids.append(uid)
        except InvalidId:
            pass
    
    # Filtre les ObjectIds valides pour les appareils
    valid_device_ids = []
    for did in device_ids:
        try:
            PydanticObjectId(did)
            valid_device_ids.append(did)
        except InvalidId:
            pass
    
    utilisateurs = await Utilisateur.find({"_id": {"$in": [PydanticObjectId(uid) for uid in valid_user_ids]}}).to_list() if valid_user_ids else []
    appareils = await Device.find({"_id": {"$in": [PydanticObjectId(did) for did in valid_device_ids]}}).to_list() if valid_device_ids else []
    username_map = {str(u.id): u.username for u in utilisateurs}
    device_map = {str(d.id): f"{d.type} ({d.numero_serie})" for d in appareils}

    return [
        DonneeEnDB(
            id=str(d.id),
            user_id=d.user_id,
            patient_nom=username_map.get(d.user_id),
            device_id=d.device_id,
            device_nom=device_map.get(d.device_id),
            frequence_cardiaque=d.frequence_cardiaque,
            pression_arterielle=d.pression_arterielle,
            taux_oxygene=d.taux_oxygene,
            date=d.date,
        ) for d in donnees
    ]
