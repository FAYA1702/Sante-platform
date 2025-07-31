"""Router Patient: résumé et historique détaillé pour la fiche patient.
Simple implémentation : agrège les données, alertes et recommandations liées au patient.
Assume que l'ID patient est l'ObjectId du document Utilisateur avec role=='patient'."""

from typing import List, Dict, Any

from beanie.operators import In
from fastapi import APIRouter, HTTPException
from backend.models.utilisateur import Utilisateur
from backend.models.donnee import Donnee
from backend.models.alerte import Alerte
from backend.models.recommandation import Recommandation
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/{patient_id}/summary")
async def patient_summary(patient_id: str) -> Dict[str, Any]:
    """Infos générales + derniers signes vitaux d'un patient."""
    oid = ObjectId(patient_id)
    patient = await Utilisateur.find_one(Utilisateur.id == oid, Utilisateur.role == "patient")
    if not patient:
        raise HTTPException(status_code=404, detail="Patient introuvable")

    last_data_docs = await Donnee.find(Donnee.user_id == oid).sort("-date").limit(1).to_list()
    last_data = last_data_docs[0] if last_data_docs else None

    return {
        "id": patient_id,
        "nom": patient.username,
        "email": patient.email,
        "last_data": last_data.dict() if last_data else None,
    }


@router.get("/{patient_id}/history")
async def patient_history(patient_id: str) -> Dict[str, Any]:
    """Historique complet : données santé, alertes, recommandations."""
    oid = ObjectId(patient_id)

    data_cursor = Donnee.find(Donnee.user_id == oid).sort("-date")
    alert_cursor = Alerte.find(Alerte.user_id == oid).sort("-date") if hasattr(Alerte, "user_id") else []
    reco_cursor = Recommandation.find(Recommandation.user_id == oid).sort("-date")

    donnees = await data_cursor.to_list()
    alertes = await alert_cursor.to_list() if alert_cursor else []
    recos = await reco_cursor.to_list()

    recommandations_list = [r.dict() for r in recos]

    return {
        "donnees": [d.dict() for d in donnees],
        "alertes": [a.dict() for a in alertes],
        "recommandations": recommandations_list
    }

