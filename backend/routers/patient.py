"""Routeur pour les fonctionnalités spécifiques aux patients."""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from backend.dependencies.auth import get_current_user
from backend.models.utilisateur import Utilisateur, Role
from backend.schemas.recommandation import RecommandationEnDB
from backend.db import get_client, MONGO_DB_NAME
from bson import ObjectId

router = APIRouter(prefix="/patient", tags=["patient"])

@router.get("/recommandations")
async def get_patient_recommandations(
    current_user=Depends(get_current_user),
    statut: Optional[str] = Query("active"),
    limit: int = Query(20, le=100)
):
    """Récupère les recommandations pour le patient connecté (compatibilité legacy)."""
    if current_user.role != Role.patient:
        raise HTTPException(status_code=403, detail="Accès réservé aux patients")

    try:
        client = get_client()
        db = client[MONGO_DB_NAME]

        patient_id = str(current_user.id)
        base_patient = {"$or": [{"patient_id": patient_id}, {"user_id": patient_id}]}

        filtre = dict(base_patient)
        if statut and statut != "all":
            if statut == "active":
                filtre = {
                    **base_patient,
                    "$or": [
                        {"statut": "active"},
                        {"statut": {"$exists": False}, "is_active": True},
                        {"statut": {"$exists": False}, "is_active": {"$exists": False}},
                    ],
                }
            else:
                filtre["statut"] = statut

        cursor = db.recommandations.find(filtre).sort("date_creation", -1).limit(limit)
        recos = await cursor.to_list(None)

        # Mapping minimal attendu côté frontend patient
        def fmt(r: dict) -> dict:
            return {
                "id": str(r.get("_id")),
                "titre": r.get("titre", "Recommandation"),
                "description": r.get("description", ""),
                "priorite": r.get("priorite", "moyenne"),
                "statut": r.get("statut", "active"),
                "type": r.get("type", "generale"),
                "date_creation": r.get("date_creation", datetime.utcnow()).isoformat()
                    if isinstance(r.get("date_creation"), datetime) else str(r.get("date_creation", "")),
                "vue_patient": r.get("vue_patient", False),
                "alerte_liee": bool(r.get("alerte_id")),
                "medecin": {"nom": r.get("medecin_nom", "Dr. Inconnu"), "department": r.get("department", "Médecine générale")},
            }

        return {"recommandations": [fmt(r) for r in recos], "total": len(recos), "statut_filtre": statut or "all"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des recommandations: {str(e)}")

@router.get("/notifications/recommandations")
async def get_patient_notifications(current_user=Depends(get_current_user)):
    """Récupère les notifications de recommandations pour le patient (compat)."""
    if current_user.role != Role.patient:
        raise HTTPException(status_code=403, detail="Accès réservé aux patients")

    try:
        client = get_client()
        db = client[MONGO_DB_NAME]

        patient_id = str(current_user.id)
        base_patient = {"$or": [{"patient_id": patient_id}, {"user_id": patient_id}]}

        non_vues = await db.recommandations.count_documents({
            **base_patient,
            "vue_patient": False,
            "$or": [
                {"statut": "active"},
                {"statut": {"$exists": False}, "is_active": True},
                {"statut": {"$exists": False}, "is_active": {"$exists": False}},
            ],
        })

        total = await db.recommandations.count_documents(base_patient)

        return {"non_lues": non_vues, "total": total}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des notifications: {str(e)}")


@router.get("/medecin-referent")
async def get_medecin_referent(current_user=Depends(get_current_user)):
    """Récupère les informations du médecin référent du patient connecté."""
    if current_user.role != Role.patient:
        raise HTTPException(status_code=403, detail="Accès réservé aux patients")
    
    # Vérifier si le patient a des médecins assignés
    if not current_user.medecin_ids:
        raise HTTPException(status_code=404, detail="Aucun médecin référent assigné")
    
    # Récupérer le premier médecin (relation 1:1 selon RBAC)
    medecin_id = current_user.medecin_ids[0]
    
    try:
        medecin = await Utilisateur.find_one(
            Utilisateur.id == ObjectId(medecin_id),
            Utilisateur.role == Role.medecin
        )
        
        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin référent introuvable")
        
        # Retourner les informations du médecin (sans données sensibles)
        return {
            "id": str(medecin.id),
            "username": medecin.username,
            "email": medecin.email,
            "nom": getattr(medecin, 'nom', None),
            "prenom": getattr(medecin, 'prenom', None),
            "department_id": getattr(medecin, 'department_id', None),
            "statut": getattr(medecin, 'statut', None)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/profile")
async def get_patient_profile(current_user=Depends(get_current_user)):
    """Récupère le profil complet du patient connecté."""
    if current_user.role != Role.patient:
        raise HTTPException(status_code=403, detail="Accès réservé aux patients")
    
    # Informations de base du patient
    profile = {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "is_active": current_user.is_active
    }
    
    # Ajouter les informations du médecin référent si disponible
    if current_user.medecin_ids:
        try:
            medecin_id = current_user.medecin_ids[0]
            medecin = await Utilisateur.find_one(
                Utilisateur.id == ObjectId(medecin_id),
                Utilisateur.role == Role.medecin
            )
            
            if medecin:
                profile["medecin_referent"] = {
                    "id": str(medecin.id),
                    "username": medecin.username,
                    "nom": getattr(medecin, 'nom', None),
                    "prenom": getattr(medecin, 'prenom', None),
                    "department_id": getattr(medecin, 'department_id', None)
                }
        except Exception:
            # Si erreur, continuer sans le médecin référent
            pass
    
    return profile


@router.put("/recommandations/{recommandation_id}/statut")
async def update_recommandation_statut(
    recommandation_id: str,
    nouveau_statut: str = Query(..., description="Nouveau statut (active, en_cours, terminee)"),
    current_user=Depends(get_current_user)
):
    """Permet au patient de mettre à jour le statut d'une recommandation (compat patient_id/user_id)."""
    if current_user.role != Role.patient:
        raise HTTPException(status_code=403, detail="Accès réservé aux patients")

    try:
        client = get_client()
        db = client[MONGO_DB_NAME]

        patient_id = str(current_user.id)
        base_patient = {"$or": [{"patient_id": patient_id}, {"user_id": patient_id}]}

        # Vérifier que la reco appartient au patient
        reco = await db.recommandations.find_one({"_id": ObjectId(recommandation_id), **base_patient})
        if not reco:
            raise HTTPException(status_code=404, detail="Recommandation introuvable")

        # Statuts autorisés
        if nouveau_statut not in ["active", "en_cours", "terminee"]:
            raise HTTPException(status_code=400, detail="Statut non autorisé (active, en_cours, terminee)")

        result = await db.recommandations.update_one(
            {"_id": ObjectId(recommandation_id)},
            {"$set": {"statut": nouveau_statut, "date_maj_patient": datetime.utcnow()}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Aucune mise à jour effectuée")

        return {"success": True, "recommandation_id": recommandation_id, "nouveau_statut": nouveau_statut}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")
