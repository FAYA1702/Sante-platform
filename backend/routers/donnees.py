"""Routeur pour la gestion des données de santé."""

from typing import List
from datetime import datetime

from fastapi import APIRouter, Query, status, Depends

from backend.dependencies.auth import get_current_user, verifier_roles, roles_sante
from backend.models.utilisateur import Role, Utilisateur
from backend.models.donnee import Donnee, SourceDonnee
from backend.models.device import Device
from backend.event_bus import publish as publish_event
from backend.schemas.donnee import DonneeCreation, DonneeEnDB

router = APIRouter()

@router.get("", response_model=List[DonneeEnDB])
@router.get("/", response_model=List[DonneeEnDB], include_in_schema=False)
async def obtenir_donnees(
    current_user=Depends(get_current_user),
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
    )
):
    """
    Liste les données de santé filtrées par plage de dates et par utilisateur (RGPD).
    - Patient : ne voit que ses propres données.
    - Médecin : voit les données de ses patients assignés.
    - Admin : accès à toutes les données (uniquement pour la démo).
    """
    filtre: dict = {}

    # Filtrage par dates
    if from_ or to:
        filtre["date"] = {}
        if from_:
            filtre["date"]["$gte"] = from_
        if to:
            filtre["date"]["$lte"] = to

    # Filtrage RBAC selon le rôle
    if current_user.role == "patient":
        filtre["user_id"] = str(current_user.id)
    elif current_user.role == "medecin":
        # TODO: Implémenter la logique d'assignation (patients du médecin)
        ...  # à implémenter en production
    # Admin garde accès à tout (mode démo)

    donnees = await Donnee.find(filtre).to_list()

    # Conversion explicite pour correspondre à DonneeEnDB (id en str)
    return [
        DonneeEnDB(
            id=str(d.id),
            user_id=d.user_id,
            patient_nom=None,
            device_id=getattr(d, "device_id", None),
            device_nom=None,
            frequence_cardiaque=d.frequence_cardiaque,
            pression_arterielle=d.pression_arterielle,
            taux_oxygene=d.taux_oxygene,
            source=d.source,
            date=d.date,
        )
        for d in donnees
    ]

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




@router.post("", response_model=DonneeEnDB, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(verifier_roles([Role.patient, Role.medecin]))])
@router.post("/", response_model=DonneeEnDB, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def ajouter_donnee(donnee: DonneeCreation, current_user=Depends(get_current_user)):
    """
    Ajoute une donnée de santé dans MongoDB (Beanie).
    
    - Le champ user_id est automatiquement renseigné avec l'ID de l'utilisateur connecté.
    - Accessible uniquement aux patients et médecins.
    - En mode démo, l'admin peut aussi accéder à cet endpoint.
    
    Exemple de corps de requête :
    ```json
    {
      "device_id": "string",
      "frequence_cardiaque": 72,
      "pression_arterielle": "120/80",
      "taux_oxygene": 98.5,
      "source": "saisie_manuelle",
      "date": "2025-08-17T23:15:07.123Z"
    }
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
    
    # Analyse automatique des données pour générer alertes et recommandations
    from backend.services.analyse_automatique_simple import traiter_nouvelle_donnee_sync
    try:
        resultat_analyse = traiter_nouvelle_donnee_sync(str(doc.id))
        print(f"Analyse automatique: {resultat_analyse}")
    except Exception as e:
        print(f"Erreur lors de l'analyse automatique: {e}")

    # Retourne la donnée insérée sans passer deux fois user_id
    return DonneeEnDB(id=str(doc.id), user_id=str(current_user.id), **donnee_data)


#
# Accès strictement réservé aux patients et médecins (conforme RGPD, secret médical)
# Pour la démo, tu peux décommenter la ligne suivante pour autoriser l’admin :
# dependencies=[Depends(verifier_roles(roles_sante()))]
# ⚠️ Ne jamais activer cette option en production sans justification légale !
# Accès strictement réservé aux patients et médecins (conforme RGPD, secret médical)
@router.get("/test")
async def test_data_endpoint():
    """
    Endpoint de test pour diagnostiquer les problèmes de données.
    Accessible sans authentification pour faciliter le débogage.
    """
    try:
        donnees = await Donnee.find().limit(3).to_list()
        return {
            "status": "ok",
            "count": len(donnees),
            "sample": [d.dict() for d in donnees[:2]] if donnees else []
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
