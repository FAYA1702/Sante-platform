"""
Routeur d'administration pour la gestion des utilisateurs et validations.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from beanie import PydanticObjectId
from backend.models.utilisateur import Utilisateur, Role, StatutUtilisateur
from backend.dependencies.auth import verifier_roles, get_current_user

router = APIRouter()

@router.get("/medecins-en-attente", dependencies=[Depends(verifier_roles([Role.admin]))])
async def lister_medecins_en_attente():
    """Liste tous les médecins en attente de validation."""
    try:
        medecins_en_attente = await Utilisateur.find({
            "role": Role.medecin,
            "statut": StatutUtilisateur.en_attente
        }).to_list()
        
        # Formater les données pour le frontend
        result = []
        for medecin in medecins_en_attente:
            result.append({
                "id": str(medecin.id),
                "username": medecin.username,
                "email": medecin.email,
                "department_id": medecin.department_id or "Non spécifié",
                "created_at": medecin.created_at.isoformat(),
                "statut": medecin.statut
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des médecins en attente: {str(e)}")

@router.patch("/medecins/{medecin_id}/approuver", dependencies=[Depends(verifier_roles([Role.admin]))])
async def approuver_medecin(medecin_id: str):
    """Approuve un médecin en attente et l'active."""
    try:
        # Convertir l'ID en ObjectId
        try:
            object_id = PydanticObjectId(medecin_id)
        except Exception:
            raise HTTPException(status_code=400, detail="ID médecin invalide")
        
        # Rechercher le médecin
        medecin = await Utilisateur.find_one({
            "_id": object_id,
            "role": Role.medecin,
            "statut": StatutUtilisateur.en_attente
        })
        
        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin en attente introuvable")
        
        # Changer le statut à actif
        medecin.statut = StatutUtilisateur.actif
        await medecin.save()
        
        print(f"[ADMIN] Médecin {medecin.username} approuvé et activé")
        
        return {
            "message": f"Le Dr. {medecin.username} a été approuvé avec succès",
            "medecin_id": medecin_id,
            "nouveau_statut": StatutUtilisateur.actif
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'approbation: {str(e)}")

@router.patch("/medecins/{medecin_id}/rejeter", dependencies=[Depends(verifier_roles([Role.admin]))])
async def rejeter_medecin(medecin_id: str):
    """Rejette un médecin en attente et le suspend."""
    try:
        # Convertir l'ID en ObjectId
        try:
            object_id = PydanticObjectId(medecin_id)
        except Exception:
            raise HTTPException(status_code=400, detail="ID médecin invalide")
        
        # Rechercher le médecin
        medecin = await Utilisateur.find_one({
            "_id": object_id,
            "role": Role.medecin,
            "statut": StatutUtilisateur.en_attente
        })
        
        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin en attente introuvable")
        
        # Changer le statut à suspendu
        medecin.statut = StatutUtilisateur.suspendu
        await medecin.save()
        
        print(f"[ADMIN] Médecin {medecin.username} rejeté et suspendu")
        
        return {
            "message": f"Le Dr. {medecin.username} a été rejeté",
            "medecin_id": medecin_id,
            "nouveau_statut": StatutUtilisateur.suspendu
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du rejet: {str(e)}")

@router.get("/medecins-actifs", dependencies=[Depends(verifier_roles([Role.admin]))])
async def lister_medecins_actifs():
    """Liste tous les médecins actifs."""
    try:
        medecins_actifs = await Utilisateur.find({
            "role": Role.medecin,
            "statut": StatutUtilisateur.actif
        }).to_list()
        
        result = []
        for medecin in medecins_actifs:
            result.append({
                "id": str(medecin.id),
                "username": medecin.username,
                "email": medecin.email,
                "department_id": medecin.department_id or "Non spécifié",
                "nb_patients": len(medecin.patient_ids),
                "created_at": medecin.created_at.isoformat(),
                "statut": medecin.statut
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des médecins actifs: {str(e)}")

@router.patch("/medecins/{medecin_id}/suspendre", dependencies=[Depends(verifier_roles([Role.admin]))])
async def suspendre_medecin(medecin_id: str):
    """Suspend un médecin actif."""
    try:
        # Convertir l'ID en ObjectId
        try:
            object_id = PydanticObjectId(medecin_id)
        except Exception:
            raise HTTPException(status_code=400, detail="ID médecin invalide")
        
        medecin = await Utilisateur.find_one({
            "_id": object_id,
            "role": Role.medecin,
            "statut": StatutUtilisateur.actif
        })
        
        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin actif introuvable")
        
        medecin.statut = StatutUtilisateur.suspendu
        await medecin.save()
        
        print(f"[ADMIN] Médecin {medecin.username} suspendu")
        
        return {
            "message": f"Le Dr. {medecin.username} a été suspendu",
            "medecin_id": medecin_id,
            "nouveau_statut": StatutUtilisateur.suspendu
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suspension: {str(e)}")

@router.patch("/medecins/{medecin_id}/reactiver", dependencies=[Depends(verifier_roles([Role.admin]))])
async def reactiver_medecin(medecin_id: str):
    """Réactive un médecin suspendu."""
    try:
        # Convertir l'ID en ObjectId
        try:
            object_id = PydanticObjectId(medecin_id)
        except Exception:
            raise HTTPException(status_code=400, detail="ID médecin invalide")
        
        medecin = await Utilisateur.find_one({
            "_id": object_id,
            "role": Role.medecin,
            "statut": StatutUtilisateur.suspendu
        })
        
        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin suspendu introuvable")
        
        medecin.statut = StatutUtilisateur.actif
        await medecin.save()
        
        print(f"[ADMIN] Médecin {medecin.username} réactivé")
        
        return {
            "message": f"Le Dr. {medecin.username} a été réactivé",
            "medecin_id": medecin_id,
            "nouveau_statut": StatutUtilisateur.actif
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la réactivation: {str(e)}")
