"""Routeur FastAPI pour la gestion des orientations médicales (referrals).
Tous les commentaires sont rédigés en français.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from beanie import PydanticObjectId
from ..models import Referral, Assignment, Utilisateur, Department
from ..schemas.referral import (
    ReferralCreate, ReferralUpdate, ReferralResponse,
    AssignmentCreate, AssignmentUpdate, AssignmentResponse
)
from ..dependencies.auth import get_current_user, require_role
from datetime import datetime

router = APIRouter(prefix="/referrals", tags=["Orientations"])


@router.get("/", response_model=List[ReferralResponse])
@router.get("", response_model=List[ReferralResponse])
async def get_referrals(
    status_filter: Optional[str] = Query(None, description="Filtrer par statut"),
    department_id: Optional[str] = Query(None, description="Filtrer par département"),
    patient_id: Optional[str] = Query(None, description="Filtrer par patient"),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Récupérer la liste des orientations selon le rôle de l'utilisateur."""
    
    # Construire le filtre selon le rôle
    filter_query = {}
    
    if current_user.role == "patient":
        # Patient : ses propres orientations uniquement
        filter_query["patient_id"] = str(current_user.id)
    elif current_user.role == "medecin":
        # Médecin : orientations vers son département
        if current_user.department_id:
            filter_query["proposed_department_id"] = current_user.department_id
        else:
            return []  # Médecin sans département ne voit rien
    elif current_user.role == "admin":
        # Admin : toutes les orientations
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )
    
    # Appliquer les filtres optionnels
    if status_filter:
        filter_query["status"] = status_filter
    if department_id:
        filter_query["proposed_department_id"] = department_id
    if patient_id:
        filter_query["patient_id"] = patient_id
    
    referrals = await Referral.find(filter_query).to_list()
    
    # Enrichir avec les noms
    enriched_referrals = []
    for referral in referrals:
        # Récupérer le nom du patient
        patient = await Utilisateur.get(referral.patient_id)
        patient_name = patient.username if patient else "Inconnu"
        
        # Récupérer le nom du département
        department = await Department.get(referral.proposed_department_id)
        department_name = department.name if department else "Inconnu"
        
        # Récupérer le nom du créateur
        created_by_name = None
        if referral.created_by:
            creator = await Utilisateur.get(referral.created_by)
            created_by_name = creator.username if creator else "Inconnu"
        
        enriched_referrals.append(ReferralResponse(
            id=str(referral.id),
            patient_id=referral.patient_id,
            proposed_department_id=referral.proposed_department_id,
            status=referral.status,
            source=referral.source,
            notes=referral.notes,
            created_by=referral.created_by,
            processed_by=referral.processed_by,
            processed_at=referral.processed_at,
            created_at=referral.created_at,
            updated_at=referral.updated_at,
            patient_name=patient_name,
            department_name=department_name,
            created_by_name=created_by_name
        ))
    
    return enriched_referrals


@router.post("/", response_model=ReferralResponse)
@router.post("", response_model=ReferralResponse)
async def create_referral(
    referral_data: ReferralCreate,
    current_user: Utilisateur = Depends(get_current_user)
):
    """Créer une nouvelle orientation médicale."""
    
    # Vérifier que le patient existe
    patient = await Utilisateur.get(referral_data.patient_id)
    if not patient or patient.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    # Vérifier que le département existe
    department = await Department.get(referral_data.proposed_department_id)
    if not department or not department.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Département non trouvé ou inactif"
        )
    
    # Créer l'orientation
    referral = Referral(
        patient_id=referral_data.patient_id,
        proposed_department_id=referral_data.proposed_department_id,
        source=referral_data.source,
        notes=referral_data.notes,
        created_by=str(current_user.id)
    )
    
    await referral.insert()
    
    return ReferralResponse(
        id=str(referral.id),
        patient_id=referral.patient_id,
        proposed_department_id=referral.proposed_department_id,
        status=referral.status,
        source=referral.source,
        notes=referral.notes,
        created_by=referral.created_by,
        processed_by=referral.processed_by,
        processed_at=referral.processed_at,
        created_at=referral.created_at,
        updated_at=referral.updated_at,
        patient_name=patient.username,
        department_name=department.name,
        created_by_name=current_user.username
    )


@router.patch("/{referral_id}", response_model=ReferralResponse)
async def update_referral(
    referral_id: str,
    referral_data: ReferralUpdate,
    current_user: Utilisateur = Depends(get_current_user)
):
    """Mettre à jour une orientation (accepter, refuser, etc.)."""
    
    referral = await Referral.get(referral_id)
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orientation non trouvée"
        )
    
    # Vérifier les permissions
    if current_user.role == "medecin":
        # Médecin : peut traiter les orientations vers son département
        if referral.proposed_department_id != current_user.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez traiter que les orientations vers votre département"
            )
    elif current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les médecins et admins peuvent traiter les orientations"
        )
    
    # Mettre à jour les champs
    if referral_data.status is not None:
        referral.status = referral_data.status
        referral.processed_by = str(current_user.id)
        referral.processed_at = datetime.utcnow()
    
    if referral_data.notes is not None:
        referral.notes = referral_data.notes
    
    referral.updated_at = datetime.utcnow()
    await referral.save()
    
    # Si acceptée, créer automatiquement une assignation
    if referral_data.status == "accepted" and current_user.role == "medecin":
        # Vérifier qu'il n'y a pas déjà une assignation active pour ce patient
        existing_assignment = await Assignment.find_one({
            "patient_id": referral.patient_id,
            "status": "active"
        })
        
        if not existing_assignment:
            assignment = Assignment(
                patient_id=referral.patient_id,
                department_id=referral.proposed_department_id,
                doctor_id=str(current_user.id),
                referral_id=str(referral.id),
                created_by=str(current_user.id)
            )
            await assignment.insert()
            
            # Mettre à jour le patient avec l'assignation
            patient = await Utilisateur.get(referral.patient_id)
            if patient:
                patient.current_assignment_id = str(assignment.id)
                await patient.save()
    
    # Enrichir la réponse
    patient = await Utilisateur.get(referral.patient_id)
    department = await Department.get(referral.proposed_department_id)
    
    return ReferralResponse(
        id=str(referral.id),
        patient_id=referral.patient_id,
        proposed_department_id=referral.proposed_department_id,
        status=referral.status,
        source=referral.source,
        notes=referral.notes,
        created_by=referral.created_by,
        processed_by=referral.processed_by,
        processed_at=referral.processed_at,
        created_at=referral.created_at,
        updated_at=referral.updated_at,
        patient_name=patient.username if patient else "Inconnu",
        department_name=department.name if department else "Inconnu",
        created_by_name=current_user.username
    )
