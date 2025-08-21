"""
Router pour les recommandations côté patient
Permet aux patients de récupérer leurs recommandations médicales
"""

from typing import List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from backend.dependencies.auth import get_current_user
from backend.models.utilisateur import Role
from backend.db import get_client, MONGO_DB_NAME
from bson import ObjectId

router = APIRouter(prefix="/patient", tags=["patient-recommandations"])


@router.get("/recommandations")
async def get_patient_recommandations(
    statut: str = Query("active", description="Statut des recommandations (active, terminee, archivee)"),
    limit: int = Query(50, description="Nombre maximum de recommandations à retourner"),
    current_user=Depends(get_current_user)
):
    """
    Récupère les recommandations du patient connecté.
    Seuls les patients peuvent accéder à cette route.
    """
    if current_user.role != Role.patient:
        raise HTTPException(status_code=403, detail="Accès réservé aux patients")
    
    try:
        # Connexion MongoDB directe
        client = get_client()
        db = client[MONGO_DB_NAME]
        
        patient_id = str(current_user.id)
        
        # Construire le filtre: compatibilité patient_id OU user_id (legacy)
        base_patient_filter = {"$or": [{"patient_id": patient_id}, {"user_id": patient_id}]}
        filtre = dict(base_patient_filter)
        if statut != "all":
            if statut == "active":
                # Inclure aussi les documents sans champ 'statut' mais actifs (legacy)
                filtre = {
                    **base_patient_filter,
                    "$or": [
                        {"statut": "active"},
                        {"statut": {"$exists": False}, "is_active": True},
                        {"statut": {"$exists": False}, "is_active": {"$exists": False}}
                    ]
                }
            else:
                filtre["statut"] = statut
        
        # Récupérer les recommandations
        recommandations_cursor = db.recommandations.find(filtre).sort("date_creation", -1).limit(limit)
        recommandations = await recommandations_cursor.to_list(None)
        
        # Enrichir avec les informations du médecin
        medecin_ids = list(set([r.get('medecin_id') for r in recommandations if r.get('medecin_id')]))
        medecins = {}
        
        if medecin_ids:
            medecins_cursor = db.utilisateurs.find({
                "_id": {"$in": [ObjectId(mid) for mid in medecin_ids]},
                "role": "medecin"
            })
            medecins_docs = await medecins_cursor.to_list(None)
            medecins = {str(m['_id']): m for m in medecins_docs}
        
        # Formater les recommandations pour le patient
        recommandations_formatees = []
        for reco in recommandations:
            medecin_info = medecins.get(reco.get('medecin_id', ''), {})
            
            reco_formatee = {
                "id": str(reco['_id']),
                "titre": reco.get('titre', 'Recommandation'),
                "description": reco.get('description', ''),
                "priorite": reco.get('priorite', 'moyenne'),
                "statut": reco.get('statut', 'active'),
                "type": reco.get('type', 'generale'),
                "date_creation": reco.get('date_creation', datetime.utcnow()).isoformat() if isinstance(reco.get('date_creation'), datetime) else str(reco.get('date_creation', '')),
                "date_limite": reco.get('date_limite', ''),
                "vue_patient": reco.get('vue_patient', False),
                "medecin": {
                    "nom": medecin_info.get('username', 'Dr. Inconnu'),
                    "department": medecin_info.get('department_id', 'Médecine générale')
                },
                "alerte_liee": bool(reco.get('alerte_id'))
            }
            
            recommandations_formatees.append(reco_formatee)
        
        # Marquer les recommandations comme vues par le patient
        if recommandations:
            reco_ids = [ObjectId(r['_id']) for r in recommandations]
            await db.recommandations.update_many(
                {"_id": {"$in": reco_ids}},
                {"$set": {"vue_patient": True, "date_vue_patient": datetime.utcnow()}}
            )
        
        return {
            "recommandations": recommandations_formatees,
            "total": len(recommandations_formatees),
            "statut_filtre": statut
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des recommandations: {str(e)}")


@router.put("/recommandations/{recommandation_id}/statut")
async def update_recommandation_statut(
    recommandation_id: str,
    nouveau_statut: str = Query(..., description="Nouveau statut (active, en_cours, terminee)"),
    current_user=Depends(get_current_user)
):
    """
    Permet au patient de mettre à jour le statut d'une de ses recommandations.
    """
    if current_user.role != Role.patient:
        raise HTTPException(status_code=403, detail="Accès réservé aux patients")
    
    try:
        client = get_client()
        db = client[MONGO_DB_NAME]
        
        patient_id = str(current_user.id)
        
        # Vérifier que la recommandation appartient au patient
        recommandation = await db.recommandations.find_one({
            "_id": ObjectId(recommandation_id),
            "patient_id": patient_id
        })
        
        if not recommandation:
            raise HTTPException(status_code=404, detail="Recommandation introuvable")
        
        # Statuts autorisés pour le patient
        statuts_autorises = ["active", "en_cours", "terminee"]
        if nouveau_statut not in statuts_autorises:
            raise HTTPException(status_code=400, detail=f"Statut non autorisé. Statuts autorisés: {statuts_autorises}")
        
        # Mettre à jour le statut
        result = await db.recommandations.update_one(
            {"_id": ObjectId(recommandation_id)},
            {
                "$set": {
                    "statut": nouveau_statut,
                    "date_maj_patient": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Impossible de mettre à jour la recommandation")
        
        return {
            "success": True,
            "message": f"Statut mis à jour vers '{nouveau_statut}'",
            "recommandation_id": recommandation_id,
            "nouveau_statut": nouveau_statut
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.get("/notifications/recommandations")
async def get_notifications_recommandations(
    current_user=Depends(get_current_user)
):
    """
    Récupère les notifications de nouvelles recommandations pour le patient.
    """
    if current_user.role != Role.patient:
        raise HTTPException(status_code=403, detail="Accès réservé aux patients")
    
    try:
        client = get_client()
        db = client[MONGO_DB_NAME]
        
        patient_id = str(current_user.id)
        
        # Compter les recommandations non vues
        recommandations_non_vues = await db.recommandations.count_documents({
            **base_patient_filter,
            "vue_patient": False,
            "$or": [
                {"statut": "active"},
                {"statut": {"$exists": False}, "is_active": True},
                {"statut": {"$exists": False}, "is_active": {"$exists": False}}
            ]
        })
        
        # Récupérer les dernières recommandations non vues
        dernieres_recommandations = await db.recommandations.find({
            **base_patient_filter,
            "vue_patient": False,
            "$or": [
                {"statut": "active"},
                {"statut": {"$exists": False}, "is_active": True},
                {"statut": {"$exists": False}, "is_active": {"$exists": False}}
            ]
        }).sort("date_creation", -1).limit(5).to_list(None)
        
        notifications = []
        for reco in dernieres_recommandations:
            notifications.append({
                "id": str(reco['_id']),
                "titre": reco.get('titre', 'Nouvelle recommandation'),
                "priorite": reco.get('priorite', 'moyenne'),
                "type": reco.get('type', 'generale'),
                "date_creation": reco.get('date_creation', datetime.utcnow()).isoformat() if isinstance(reco.get('date_creation'), datetime) else str(reco.get('date_creation', ''))
            })
        
        return {
            "total_non_vues": recommandations_non_vues,
            "notifications": notifications
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des notifications: {str(e)}")
