"""
Routeur pour la gestion des assignations patient-médecin.
Permet l'assignation, la désassignation et la consultation des relations médicales.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId

from backend.dependencies.auth import get_current_user, verifier_roles
from backend.models.utilisateur import Utilisateur, Role
from backend.schemas.assignation import (
    AssignationRequest, 
    AssignationResponse, 
    ListePatients, 
    ListeMedecins
)

router = APIRouter(prefix="/assignation", tags=["assignation"])


# -----------------------------------------------------------------------------
# Endpoints pour les PATIENTS
# -----------------------------------------------------------------------------

@router.get("/mes-medecins", response_model=ListeMedecins)
async def lister_mes_medecins(current_user=Depends(get_current_user)):
    """Liste les médecins assignés au patient connecté."""
    if current_user.role != Role.patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les patients peuvent consulter leurs médecins"
        )
    
    # Récupérer les médecins assignés
    medecin_ids = [PydanticObjectId(mid) for mid in current_user.medecin_ids]
    medecins = await Utilisateur.find({"_id": {"$in": medecin_ids}}).to_list() if medecin_ids else []
    
    return ListeMedecins(
        medecins=[
            {
                "id": str(m.id),
                "username": m.username,
                "email": m.email,
                "specialite": "Médecin généraliste"  # À étendre avec un champ spécialité
            }
            for m in medecins
        ]
    )


@router.post("/demander-assignation", response_model=AssignationResponse)
async def demander_assignation_medecin(
    request: AssignationRequest,
    current_user=Depends(get_current_user)
):
    """Permet à un patient de demander l'assignation à un médecin."""
    if current_user.role != Role.patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les patients peuvent demander une assignation"
        )
    
    # Vérifier que le médecin existe
    medecin = await Utilisateur.get(PydanticObjectId(request.medecin_id))
    if not medecin or medecin.role != Role.medecin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médecin non trouvé"
        )
    
    # Vérifier si l'assignation existe déjà
    if request.medecin_id in current_user.medecin_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous êtes déjà assigné à ce médecin"
        )
    
    # Ajouter l'assignation côté patient
    current_user.medecin_ids.append(request.medecin_id)
    await current_user.save()
    
    # Ajouter l'assignation côté médecin
    if str(current_user.id) not in medecin.patient_ids:
        medecin.patient_ids.append(str(current_user.id))
        await medecin.save()
    
    return AssignationResponse(
        success=True,
        message=f"Assignation réussie au Dr. {medecin.username}"
    )


# -----------------------------------------------------------------------------
# Endpoints pour les MÉDECINS
# -----------------------------------------------------------------------------

@router.get("/mes-patients", response_model=ListePatients)
async def lister_mes_patients(current_user=Depends(get_current_user)):
    """Liste les patients assignés au médecin connecté."""
    if current_user.role != Role.medecin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les médecins peuvent consulter leurs patients"
        )
    
    # Récupérer les patients assignés
    patient_ids = [PydanticObjectId(pid) for pid in current_user.patient_ids]
    patients = await Utilisateur.find({"_id": {"$in": patient_ids}}).to_list() if patient_ids else []
    
    return ListePatients(
        patients=[
            {
                "id": str(p.id),
                "username": p.username,
                "email": p.email,
                "date_assignation": p.created_at.isoformat()
            }
            for p in patients
        ]
    )


@router.post("/accepter-patient", response_model=AssignationResponse)
async def accepter_patient(
    request: AssignationRequest,
    current_user=Depends(get_current_user)
):
    """Permet à un médecin d'accepter un patient (assignation manuelle)."""
    if current_user.role != Role.medecin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les médecins peuvent accepter des patients"
        )
    
    # Vérifier que le patient existe
    patient = await Utilisateur.get(PydanticObjectId(request.patient_id))
    if not patient or patient.role != Role.patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    # Vérifier si l'assignation existe déjà
    if request.patient_id in current_user.patient_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce patient est déjà assigné"
        )
    
    # Ajouter l'assignation côté médecin
    current_user.patient_ids.append(request.patient_id)
    await current_user.save()
    
    # Ajouter l'assignation côté patient
    if str(current_user.id) not in patient.medecin_ids:
        patient.medecin_ids.append(str(current_user.id))
        await patient.save()
    
    return AssignationResponse(
        success=True,
        message=f"Patient {patient.username} assigné avec succès"
    )


# -----------------------------------------------------------------------------
# Endpoints pour les ADMINS
# -----------------------------------------------------------------------------

@router.get("/tous-medecins", response_model=ListeMedecins)
async def lister_tous_medecins(current_user=Depends(verifier_roles([Role.admin, Role.patient]))):
    """Liste tous les médecins disponibles (pour assignation)."""
    medecins = await Utilisateur.find({"role": Role.medecin}).to_list()
    
    return ListeMedecins(
        medecins=[
            {
                "id": str(m.id),
                "username": m.username,
                "email": m.email,
                "specialite": "Médecin généraliste",
                "nb_patients": len(m.patient_ids)
            }
            for m in medecins
        ]
    )


@router.delete("/supprimer/{patient_id}/{medecin_id}", response_model=AssignationResponse)
async def supprimer_assignation(
    patient_id: str,
    medecin_id: str,
    current_user=Depends(verifier_roles([Role.admin]))
):
    """Supprime une assignation patient-médecin (admin uniquement)."""
    
    # Récupérer patient et médecin
    patient = await Utilisateur.get(PydanticObjectId(patient_id))
    medecin = await Utilisateur.get(PydanticObjectId(medecin_id))
    
    if not patient or not medecin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient ou médecin non trouvé"
        )
    
    # Supprimer l'assignation côté patient
    if medecin_id in patient.medecin_ids:
        patient.medecin_ids.remove(medecin_id)
        await patient.save()
    
    # Supprimer l'assignation côté médecin
    if patient_id in medecin.patient_ids:
        medecin.patient_ids.remove(patient_id)
        await medecin.save()
    
    return AssignationResponse(
        success=True,
        message="Assignation supprimée avec succès"
    )
