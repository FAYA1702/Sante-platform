"""
Routeur pour le filtrage des alertes et recommandations par rôle médical.
Implémente la logique métier de distribution selon le rôle (médecin/patient).
"""

from fastapi import APIRouter, Depends, HTTPException
from backend.models.alerte import Alerte
from backend.models.recommandation import Recommandation
from backend.models.utilisateur import Utilisateur, Role
from backend.dependencies.auth import get_current_user
from backend.db import get_client, MONGO_DB_NAME

router = APIRouter(prefix="/filtrage", tags=["Filtrage Médical"])


@router.get("/alertes/patient")
async def get_alertes_patient(
    current_user=Depends(get_current_user)
):
    """Récupère les alertes visibles pour un patient (filtrage médical)."""
    if current_user.role != Role.patient:
        raise HTTPException(status_code=403, detail="Accès réservé aux patients")
    
    # Requête MongoDB directe avec filtrage médical
    from backend.db import get_client, MONGO_DB_NAME
    client = get_client()
    db = client[MONGO_DB_NAME]
    
    # Alertes visibles par le patient uniquement
    alertes_cursor = db.alertes.find({
        "user_id": str(current_user.id),
        "visible_patient": True,  # Filtrage médical
        "statut": "nouvelle"
    }).sort("date", -1)
    alertes_docs = await alertes_cursor.to_list(None)
    
    return [
        {
            "id": str(doc["_id"]),
            "message": doc["message"],
            "niveau": doc["niveau"],
            "priorite_medicale": doc.get("priorite_medicale", "normale"),
            "date": doc["date"] if isinstance(doc["date"], str) else doc["date"].isoformat(),
            "statut": doc["statut"]
        }
        for doc in alertes_docs
    ]


@router.get("/recommandations/patient")
async def get_recommandations_patient(
    current_user=Depends(get_current_user)
):
    """Récupère les recommandations visibles pour un patient (validées par médecin)."""
    if current_user.role != Role.patient:
        raise HTTPException(status_code=403, detail="Accès réservé aux patients")
    
    # Requête MongoDB directe avec filtrage médical
    from backend.db import get_client, MONGO_DB_NAME
    client = get_client()
    db = client[MONGO_DB_NAME]
    
    # Recommandations validées par un médecin et visibles par le patient
    recos_cursor = db.recommandations.find({
        "user_id": str(current_user.id),
        "visible_patient": True,  # Filtrage médical
        "validation_medicale": True,  # Validée par médecin
        "statut": "nouvelle"
    }).sort("date", -1)
    recos_docs = await recos_cursor.to_list(None)
    
    return [
        {
            "id": str(doc["_id"]),
            "titre": doc.get("titre", "Recommandation de santé"),
            "description": doc.get("description", "Aucune description disponible"),
            "priorite_medicale": doc.get("priorite_medicale", "normale"),
            "date": doc["date"] if isinstance(doc["date"], str) else doc["date"].isoformat(),
            "statut": doc["statut"]
        }
        for doc in recos_docs
    ]


@router.get("/alertes/medecin/critiques")
async def get_alertes_critiques_medecin(
    current_user=Depends(get_current_user)
):
    """Récupère uniquement les alertes critiques pour le médecin (priorité haute)."""
    if current_user.role != Role.medecin:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins")
    
    # Récupérer les patients du médecin
    medecin_id_str = str(current_user.id)
    from backend.db import get_client, MONGO_DB_NAME
    client = get_client()
    db = client[MONGO_DB_NAME]
    
    patients_cursor = db.utilisateurs.find({
        "role": "patient",
        "medecin_ids": medecin_id_str
    })
    patients_docs = await patients_cursor.to_list(None)
    
    if not patients_docs:
        return []
    
    patient_ids = [str(doc["_id"]) for doc in patients_docs]
    patient_map = {str(doc["_id"]): doc["username"] for doc in patients_docs}
    
    # Alertes critiques uniquement
    alertes_cursor = db.alertes.find({
        "user_id": {"$in": patient_ids},
        "priorite_medicale": {"$in": ["critique", "elevee"]},  # Priorité haute
        "statut": "nouvelle"
    }).sort("date", -1)
    alertes_docs = await alertes_cursor.to_list(None)
    
    return [
        {
            "id": str(doc["_id"]),
            "user_id": doc["user_id"],
            "message": doc["message"],
            "niveau": doc["niveau"],
            "priorite_medicale": doc.get("priorite_medicale", "normale"),
            "date": doc["date"] if isinstance(doc["date"], str) else doc["date"].isoformat(),
            "statut": doc["statut"],
            "patient_nom": patient_map.get(doc["user_id"], "Patient inconnu")
        }
        for doc in alertes_docs
    ]


@router.patch("/recommandation/{reco_id}/valider")
async def valider_recommandation_medecin(
    reco_id: str,
    visible_patient: bool = True,
    current_user=Depends(get_current_user)
):
    """Permet au médecin de valider une recommandation et la rendre visible au patient."""
    if current_user.role != Role.medecin:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins")
    
    from backend.db import get_client, MONGO_DB_NAME
    from bson import ObjectId
    
    client = get_client()
    db = client[MONGO_DB_NAME]
    
    # Mettre à jour la recommandation
    result = await db.recommandations.update_one(
        {"_id": ObjectId(reco_id)},
        {
            "$set": {
                "validation_medicale": True,
                "visible_patient": visible_patient,
                "vue_par": str(current_user.id),
                "statut": "validee"
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Recommandation non trouvée")
    
    return {"message": "Recommandation validée avec succès", "visible_patient": visible_patient}
