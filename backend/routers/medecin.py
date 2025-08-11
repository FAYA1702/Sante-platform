"""Routeur pour les fonctionnalités spécifiques aux médecins."""

from typing import List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from backend.dependencies.auth import get_current_user, verifier_roles
from backend.models.utilisateur import Utilisateur, Role
from backend.models.alerte import Alerte
from backend.models.recommandation import Recommandation
from backend.models.donnee import Donnee

router = APIRouter(prefix="/medecin", tags=["medecin"])


@router.get("/patients")
async def get_medecin_patients(current_user=Depends(get_current_user)):
    """Récupère la liste des patients assignés au médecin connecté."""
    if current_user.role != Role.medecin:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins")
    
    # Récupérer les patients assignés à ce médecin
    medecin_id_str = str(current_user.id)
    
    # Requête MongoDB directe pour éviter les problèmes avec Beanie
    from motor.motor_asyncio import AsyncIOMotorClient
    from backend.db import get_client, MONGO_DB_NAME
    
    client = get_client()
    db = client[MONGO_DB_NAME]
    
    patients_cursor = db.utilisateurs.find({
        "role": "patient",
        "medecin_ids": medecin_id_str
    })
    patients_docs = await patients_cursor.to_list(None)
    
    patients = []
    for doc in patients_docs:
        patients.append({
            "id": str(doc["_id"]),
            "username": doc["username"],
            "email": doc["email"],
            "created_at": doc["created_at"].isoformat() if "created_at" in doc else ""
        })
    
    return patients


@router.get("/alertes")
async def get_medecin_alertes(
    statut: str = "nouvelle",
    patient_id: str = None,
    current_user=Depends(get_current_user)
):
    """Récupère les alertes des patients du médecin selon le statut."""
    if current_user.role != Role.medecin:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins")
    
    # Récupérer les IDs des patients du médecin avec requête MongoDB directe
    medecin_id_str = str(current_user.id)
    
    from backend.db import get_client, MONGO_DB_NAME
    client = get_client()
    db = client[MONGO_DB_NAME]
    
    # Récupérer les patients du médecin
    patients_cursor = db.utilisateurs.find({
        "role": "patient",
        "medecin_ids": medecin_id_str
    })
    patients_docs = await patients_cursor.to_list(None)
    
    if not patients_docs:
        return []
    
    patient_ids = [str(doc["_id"]) for doc in patients_docs]
    patient_map = {str(doc["_id"]): doc["username"] for doc in patients_docs}
    
    # Filtrer par patient spécifique si demandé
    if patient_id:
        if patient_id not in patient_ids:
            raise HTTPException(status_code=403, detail="Patient non assigné à ce médecin")
        patient_ids = [patient_id]
    
    # Récupérer les alertes des patients avec le statut demandé
    alertes_cursor = db.alertes.find({
        "user_id": {"$in": patient_ids},
        "statut": statut
    }).sort("date", -1)
    alertes_docs = await alertes_cursor.to_list(None)
    
    return [
        {
            "id": str(doc["_id"]),
            "user_id": doc["user_id"],
            "message": doc["message"],
            "niveau": doc["niveau"],
            "date": doc["date"] if isinstance(doc["date"], str) else doc["date"].isoformat(),
            "statut": doc["statut"],
            "patient_nom": patient_map.get(doc["user_id"], "Patient inconnu")
        }
        for doc in alertes_docs
    ]


@router.get("/recommandations")
async def get_medecin_recommandations(
    statut: str = "nouvelle",
    patient_id: str = None,
    current_user=Depends(get_current_user)
):
    """Récupère les recommandations des patients du médecin selon le statut."""
    print(f"[DEBUG] Médecin connecté: {current_user.username} (ID: {current_user.id}, Role: {current_user.role})")
    
    if current_user.role != Role.medecin:
        print(f"[DEBUG] Accès refusé - Role: {current_user.role} != {Role.medecin}")
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins")
    
    # Récupérer les IDs des patients du médecin avec requête MongoDB directe
    medecin_id_str = str(current_user.id)
    
    from backend.db import get_client, MONGO_DB_NAME
    client = get_client()
    db = client[MONGO_DB_NAME]
    
    # Récupérer les patients du médecin
    patients_cursor = db.utilisateurs.find({
        "role": "patient",
        "medecin_ids": medecin_id_str
    })
    patients_docs = await patients_cursor.to_list(None)
    
    if not patients_docs:
        return []
    
    patient_ids = [str(doc["_id"]) for doc in patients_docs]
    patient_map = {str(doc["_id"]): doc["username"] for doc in patients_docs}
    
    # Filtrer par patient spécifique si demandé
    if patient_id:
        if patient_id not in patient_ids:
            raise HTTPException(status_code=403, detail="Patient non assigné à ce médecin")
        patient_ids = [patient_id]
    
    # Récupérer les recommandations des patients avec le statut demandé
    query = {
        "user_id": {"$in": patient_ids},
        "statut": statut
    }
    print(f"[DEBUG] Requête recommandations: {query}")
    
    recos_cursor = db.recommandations.find(query).sort("date", -1)
    recos_docs = await recos_cursor.to_list(None)
    print(f"[DEBUG] Recommandations trouvées: {len(recos_docs)}")
    
    return [
        {
            "id": str(doc["_id"]),
            "user_id": doc["user_id"],
            "titre": doc.get("titre", "Recommandation de santé"),
            "description": doc.get("description", "Aucune description disponible"),
            "date": doc["date"] if isinstance(doc["date"], str) else doc["date"].isoformat(),
            "statut": doc["statut"],
            "patient_nom": patient_map.get(doc["user_id"], "Patient inconnu")
        }
        for doc in recos_docs
    ]


@router.patch("/alertes/{alerte_id}/marquer-vue")
async def marquer_alerte_vue(alerte_id: str, current_user=Depends(get_current_user)):
    """Marque une alerte comme vue par le médecin."""
    if current_user.role != Role.medecin:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins")
    
    from bson import ObjectId
    try:
        alerte = await Alerte.find_one(Alerte.id == ObjectId(alerte_id))
        if not alerte:
            raise HTTPException(status_code=404, detail="Alerte introuvable")
        
        # Vérifier que le patient appartient au médecin
        patient = await Utilisateur.find_one(Utilisateur.id == ObjectId(alerte.user_id))
        if not patient or str(current_user.id) not in patient.medecin_ids:
            raise HTTPException(status_code=403, detail="Patient non assigné à ce médecin")
        
        # Marquer comme vue
        alerte.statut = "vue"
        alerte.vue_par = str(current_user.id)
        alerte.date_vue = datetime.utcnow()
        alerte.updated_at = datetime.utcnow()
        
        await alerte.save()
        
        return {"message": "Alerte marquée comme vue"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du marquage: {str(e)}")


@router.patch("/recommandations/{reco_id}/marquer-vue")
async def marquer_recommandation_vue(reco_id: str, current_user=Depends(get_current_user)):
    """Marque une recommandation comme vue par le médecin."""
    if current_user.role != Role.medecin:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins")
    
    from bson import ObjectId
    try:
        reco = await Recommandation.find_one(Recommandation.id == ObjectId(reco_id))
        if not reco:
            raise HTTPException(status_code=404, detail="Recommandation introuvable")
        
        # Vérifier que le patient appartient au médecin
        patient = await Utilisateur.find_one(Utilisateur.id == ObjectId(reco.user_id))
        if not patient or str(current_user.id) not in patient.medecin_ids:
            raise HTTPException(status_code=403, detail="Patient non assigné à ce médecin")
        
        # Marquer comme vue
        reco.statut = "vue"
        reco.vue_par = str(current_user.id)
        reco.date_vue = datetime.utcnow()
        reco.updated_at = datetime.utcnow()
        
        await reco.save()
        
        return {"message": "Recommandation marquée comme vue"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du marquage: {str(e)}")


@router.post("/patients/{patient_id}/assign")
async def assign_patient_to_medecin(patient_id: str, current_user=Depends(get_current_user)):
    """Assigne un patient au médecin connecté."""
    if current_user.role != Role.medecin:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins")
    
    from bson import ObjectId
    try:
        patient = await Utilisateur.find_one(
            Utilisateur.id == ObjectId(patient_id),
            Utilisateur.role == Role.patient
        )
        if not patient:
            raise HTTPException(status_code=404, detail="Patient introuvable")
        
        medecin_id = str(current_user.id)
        
        # Ajouter le médecin à la liste des médecins du patient
        if medecin_id not in patient.medecin_ids:
            patient.medecin_ids.append(medecin_id)
            patient.updated_at = datetime.utcnow()
            await patient.save()
        
        # Ajouter le patient à la liste des patients du médecin
        if patient_id not in current_user.patient_ids:
            current_user.patient_ids.append(patient_id)
            current_user.updated_at = datetime.utcnow()
            await current_user.save()
        
        return {"message": f"Patient {patient.username} assigné avec succès"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'assignation: {str(e)}")


@router.post("/recommandations")
async def creer_recommandation(
    payload: Dict[str, Any],
    current_user=Depends(get_current_user)
):
    """Crée une nouvelle recommandation pour un patient."""
    if current_user.role != Role.medecin:
        raise HTTPException(status_code=403, detail="Accès réservé aux médecins")
    
    try:
        # Vérifier que le patient appartient au médecin
        patient_id = payload.get("user_id")
        if not patient_id:
            raise HTTPException(status_code=400, detail="ID patient requis")
        
        from bson import ObjectId
        patient = await Utilisateur.find_one(Utilisateur.id == ObjectId(patient_id))
        if not patient or str(current_user.id) not in patient.medecin_ids:
            raise HTTPException(status_code=403, detail="Patient non assigné à ce médecin")
        
        # Créer la recommandation
        recommandation = Recommandation(
            user_id=patient_id,
            titre=payload.get("titre", "Recommandation médicale"),
            description=payload.get("description", ""),
            statut="nouvelle",
            created_by=str(current_user.id),
            date=datetime.utcnow()
        )
        
        await recommandation.insert()
        
        return {
            "id": str(recommandation.id),
            "message": "Recommandation créée avec succès",
            "recommandation": {
                "id": str(recommandation.id),
                "user_id": recommandation.user_id,
                "titre": recommandation.titre,
                "description": recommandation.description,
                "statut": recommandation.statut,
                "date": recommandation.date.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")
