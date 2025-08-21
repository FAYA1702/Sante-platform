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
    
    # Récupérer les patients assignés à ce médecin (ségrégation RBAC)
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
    statut: str = None,  # Permettre de voir toutes les alertes par défaut
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
    
    # Construire la requête avec ou sans filtre de statut
    # Inclure les alertes actives ou sans champ is_active (anciens documents)
    query = {
        "user_id": {"$in": patient_ids},
        "$or": [
            {"is_active": True},
            {"is_active": {"$exists": False}}
        ]
    }
    if statut:
        query["statut"] = statut
    
    # Récupérer les alertes des patients
    alertes_cursor = db.alertes.find(query).sort("date", -1)
    alertes_docs = await alertes_cursor.to_list(None)
    
    print(f"[DEBUG] Médecin {current_user.username} - Patients: {len(patient_ids)}, Alertes trouvées: {len(alertes_docs)}")
    
    def _fmt_date(value):
        if not value:
            return None
        return value if isinstance(value, str) else getattr(value, "isoformat", lambda: str(value))()

    return [
        {
            "id": str(doc.get("_id")),
            "user_id": doc.get("user_id", ""),
            "message": doc.get("message", ""),
            "niveau": doc.get("niveau", "info"),
            "date": _fmt_date(doc.get("date")),
            "statut": doc.get("statut", "nouvelle"),
            "patient_nom": patient_map.get(doc.get("user_id", ""), "Patient inconnu"),
        }
        for doc in alertes_docs
    ]


@router.get("/recommandations")
async def get_medecin_recommandations(
    statut: str | None = None,
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
    
    # Récupérer les recommandations des patients avec filtre de statut optionnel
    # Uniformiser: les recommandations référencent le patient via 'patient_id'
    query = {
        "patient_id": {"$in": patient_ids}
    }
    if statut:
        query["statut"] = statut
    print(f"[DEBUG] Requête recommandations: {query}")
    
    recos_cursor = db.recommandations.find(query).sort("date_creation", -1)
    recos_docs = await recos_cursor.to_list(None)
    print(f"[DEBUG] Recommandations trouvées: {len(recos_docs)}")
    
    return [
        {
            "id": str(doc["_id"]),
            # pour compatibilité frontend, renvoyer user_id en tant que patient_id
            "user_id": doc.get("patient_id", doc.get("user_id", "")),
            "titre": doc.get("titre", "Recommandation de santé"),
            "description": doc.get("description", "Aucune description disponible"),
            "date": (doc.get("date_creation") or doc.get("date")).isoformat() if hasattr((doc.get("date_creation") or doc.get("date")), "isoformat") else str(doc.get("date_creation") or doc.get("date")),
            "statut": doc.get("statut", "active"),
            "patient_nom": patient_map.get(doc.get("patient_id", doc.get("user_id", "")), "Patient inconnu")
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
        # Récupérer via Mongo direct pour supporter patient_id
        from backend.db import get_client, MONGO_DB_NAME
        client = get_client()
        db = client[MONGO_DB_NAME]
        doc = await db.recommandations.find_one({"_id": ObjectId(reco_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Recommandation introuvable")

        patient_id = doc.get("patient_id") or doc.get("user_id")
        if not patient_id:
            raise HTTPException(status_code=400, detail="Recommandation invalide: patient manquant")

        # Vérifier que le patient appartient au médecin
        patient = await Utilisateur.find_one(Utilisateur.id == ObjectId(patient_id))
        if not patient or str(current_user.id) not in patient.medecin_ids:
            raise HTTPException(status_code=403, detail="Patient non assigné à ce médecin")

        # Marquer comme vue
        await db.recommandations.update_one(
            {"_id": ObjectId(reco_id)},
            {"$set": {"statut": "vue", "vue_par": str(current_user.id), "date_vue": datetime.utcnow(), "updated_at": datetime.utcnow()}}
        )

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
        patient_id = payload.get("patient_id") or payload.get("user_id")
        if not patient_id:
            raise HTTPException(status_code=400, detail="ID patient requis")
        
        from bson import ObjectId
        patient = await Utilisateur.find_one(Utilisateur.id == ObjectId(patient_id))
        if not patient or str(current_user.id) not in patient.medecin_ids:
            raise HTTPException(status_code=403, detail="Patient non assigné à ce médecin")
        
        # Créer la recommandation (Mongo direct pour champs supplémentaires)
        from backend.db import get_client, MONGO_DB_NAME
        client = get_client()
        db = client[MONGO_DB_NAME]
        doc = {
            "patient_id": patient_id,
            "titre": payload.get("titre", "Recommandation médicale"),
            "description": payload.get("description", ""),
            "statut": "active",
            "priorite": payload.get("priorite", "moyenne"),
            "type": payload.get("type", "generale"),
            "alerte_id": payload.get("alerte_id"),
            "medecin_id": str(current_user.id),
            "date_creation": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "vue_patient": False,
            "is_active": True,
        }
        result = await db.recommandations.insert_one(doc)

        # Archiver l'alerte liée si présente
        try:
            if doc.get("alerte_id"):
                from bson import ObjectId as _ObjectId
                await db.alertes.update_one(
                    {"_id": _ObjectId(doc["alerte_id"])},
                    {"$set": {"statut": "archivee", "is_active": False, "updated_at": datetime.utcnow()}}
                )
        except Exception as e:
            print(f"[WARN] Impossible d'archiver l'alerte liée {doc.get('alerte_id')}: {e}")

        inserted = await db.recommandations.find_one({"_id": result.inserted_id})
        return {
            "id": str(inserted["_id"]),
            "message": "Recommandation créée avec succès",
            "recommandation": {
                "id": str(inserted["_id"]),
                "user_id": inserted.get("patient_id"),
                "titre": inserted.get("titre"),
                "description": inserted.get("description"),
                "statut": inserted.get("statut", "active"),
                "date": inserted.get("date_creation").isoformat() if hasattr(inserted.get("date_creation"), "isoformat") else str(inserted.get("date_creation"))
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")
