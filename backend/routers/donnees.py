"""Routeur pour la gestion des données de santé."""

from typing import List
from datetime import datetime

from fastapi import APIRouter, Query, status, Depends

from backend.dependencies.auth import get_current_user, verifier_roles
from backend.models.utilisateur import Role
from backend.models.donnee import Donnee
from backend.event_bus import publish as publish_event
from backend.schemas.donnee import DonneeCreation, DonneeEnDB

router = APIRouter()




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
# dependencies=[Depends(verifier_roles([Role.patient, Role.medecin, Role.admin]))]
# ⚠️ Ne jamais activer cette option en production sans justification légale !
# Accès strictement réservé aux patients et médecins (conforme RGPD, secret médical)
# Pour la démo, tu peux décommenter la ligne suivante pour autoriser l’admin :
# dependencies=[Depends(verifier_roles([Role.patient, Role.medecin, Role.admin]))]
# ⚠️ Ne jamais activer cette option en production sans justification légale !
@router.get("/data", response_model=List[DonneeEnDB],
            dependencies=[Depends(verifier_roles([Role.patient, Role.medecin, Role.admin]))])
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
    return [DonneeEnDB(id=str(d.id), user_id=d.user_id, device_id=d.device_id, frequence_cardiaque=d.frequence_cardiaque,
                       pression_arterielle=d.pression_arterielle, taux_oxygene=d.taux_oxygene, date=d.date) for d in donnees]
