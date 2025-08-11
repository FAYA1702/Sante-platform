"""Router Patient: résumé et historique détaillé pour la fiche patient.
Simple implémentation : agrège les données, alertes et recommandations liées au patient.
Assume que l'ID patient est l'ObjectId du document Utilisateur avec role=='patient'."""

from typing import List, Dict, Any

from beanie.operators import In
from fastapi import APIRouter, HTTPException, Depends
from backend.dependencies.auth import get_current_user
from backend.models.utilisateur import Utilisateur, Role
from backend.models.donnee import Donnee
from backend.models.alerte import Alerte
from backend.models.recommandation import Recommandation
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/{patient_id}/summary")
async def patient_summary(patient_id: str, current_user=Depends(get_current_user)) -> Dict[str, Any]:
    """Infos générales + derniers signes vitaux d'un patient."""
    # Vérifier les permissions
    if current_user.role == Role.patient:
        # Un patient ne peut voir que ses propres données
        if str(current_user.id) != patient_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    elif current_user.role == Role.medecin:
        # Un médecin ne peut voir que ses patients assignés
        patient = await Utilisateur.find_one(Utilisateur.id == ObjectId(patient_id))
        if not patient or str(current_user.id) not in patient.medecin_ids:
            raise HTTPException(status_code=403, detail="Patient non assigné à ce médecin")
    # Admin peut voir tous les patients
    
    oid = ObjectId(patient_id)
    patient = await Utilisateur.find_one(Utilisateur.id == oid, Utilisateur.role == "patient")
    if not patient:
        raise HTTPException(status_code=404, detail="Patient introuvable")

    # CORRECTION: user_id est stocké comme string dans les données, pas ObjectId
    last_data_docs = await Donnee.find(Donnee.user_id == patient_id).sort("-date").limit(1).to_list()
    last_data = last_data_docs[0] if last_data_docs else None

    return {
        "id": patient_id,
        "nom": patient.username,
        "email": patient.email,
        "last_data": last_data.dict() if last_data else None,
    }


@router.get("/{patient_id}/history")
async def patient_history(patient_id: str, current_user=Depends(get_current_user)) -> Dict[str, Any]:
    """Historique complet : données santé, alertes, recommandations."""
    # Vérifier les permissions
    if current_user.role == Role.patient:
        # Un patient ne peut voir que ses propres données
        if str(current_user.id) != patient_id:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    elif current_user.role == Role.medecin:
        # Un médecin ne peut voir que ses patients assignés
        patient = await Utilisateur.find_one(Utilisateur.id == ObjectId(patient_id))
        if not patient or str(current_user.id) not in patient.medecin_ids:
            raise HTTPException(status_code=403, detail="Patient non assigné à ce médecin")
    # Admin peut voir tous les patients
    
    # CORRECTION: user_id est stocké comme string dans toutes les collections
    try:
        data_cursor = Donnee.find(Donnee.user_id == patient_id).sort("-date")
        alert_cursor = Alerte.find(Alerte.user_id == patient_id).sort("-date")
        reco_cursor = Recommandation.find(Recommandation.user_id == patient_id).sort("-date")

        donnees = await data_cursor.to_list()
        alertes = await alert_cursor.to_list()
        recos = await reco_cursor.to_list()

        # Sérialisation manuelle pour éviter les problèmes de datetime
        def serialize_item(item):
            """Sérialise un item en gérant les datetime."""
            if hasattr(item, 'dict'):
                try:
                    return item.dict()
                except Exception:
                    # Fallback: sérialisation manuelle
                    result = {}
                    for field_name, field_value in item.__dict__.items():
                        if field_name.startswith('_'):
                            continue
                        if hasattr(field_value, 'isoformat'):
                            result[field_name] = field_value.isoformat()
                        else:
                            result[field_name] = field_value
                    return result
            return str(item)

        return {
            "donnees": [serialize_item(d) for d in donnees],
            "alertes": [serialize_item(a) for a in alertes],
            "recommandations": [serialize_item(r) for r in recos]
        }
    except Exception as e:
        print(f"Erreur détaillée dans patient_history: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'historique: {str(e)}")

