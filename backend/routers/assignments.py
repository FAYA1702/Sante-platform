"""Routeur FastAPI pour la gestion des assignations médicales actives.
Tous les commentaires sont rédigés en français.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from beanie import PydanticObjectId
from ..models import Assignment, Utilisateur, Department
from ..schemas.referral import AssignmentCreate, AssignmentUpdate, AssignmentResponse
from ..dependencies.auth import get_current_user, require_role
from datetime import datetime

router = APIRouter(prefix="/assignments", tags=["Assignations"])


@router.get("/", response_model=List[AssignmentResponse])
async def get_assignments(
    status_filter: Optional[str] = Query(None, description="Filtrer par statut"),
    department_id: Optional[str] = Query(None, description="Filtrer par département"),
    patient_id: Optional[str] = Query(None, description="Filtrer par patient"),
    doctor_id: Optional[str] = Query(None, description="Filtrer par médecin"),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Récupérer la liste des assignations selon le rôle de l'utilisateur."""
    
    # Construire le filtre selon le rôle
    filter_query = {}
    
    if current_user.role == "patient":
        # Patient : ses propres assignations uniquement
        filter_query["patient_id"] = str(current_user.id)
    elif current_user.role == "medecin":
        # Médecin : assignations où il est le médecin responsable
        filter_query["doctor_id"] = str(current_user.id)
    elif current_user.role == "admin":
        # Admin : toutes les assignations
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
        filter_query["department_id"] = department_id
    if patient_id:
        filter_query["patient_id"] = patient_id
    if doctor_id:
        filter_query["doctor_id"] = doctor_id
    
    assignments = await Assignment.find(filter_query).to_list()
    
    # Enrichir avec les noms
    enriched_assignments = []
    for assignment in assignments:
        # Récupérer le nom du patient
        patient = await Utilisateur.get(assignment.patient_id)
        patient_name = patient.username if patient else "Inconnu"
        
        # Récupérer le nom du département
        department = await Department.get(assignment.department_id)
        department_name = department.name if department else "Inconnu"
        
        # Récupérer le nom du médecin
        doctor = await Utilisateur.get(assignment.doctor_id)
        doctor_name = doctor.username if doctor else "Inconnu"
        
        # Récupérer le nom du créateur
        created_by_name = None
        if assignment.created_by:
            creator = await Utilisateur.get(assignment.created_by)
            created_by_name = creator.username if creator else "Inconnu"
        
        enriched_assignments.append(AssignmentResponse(
            id=str(assignment.id),
            patient_id=assignment.patient_id,
            department_id=assignment.department_id,
            doctor_id=assignment.doctor_id,
            referral_id=assignment.referral_id,
            status=assignment.status,
            notes=assignment.notes,
            start_at=assignment.start_at,
            end_at=assignment.end_at,
            created_by=assignment.created_by,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
            patient_name=patient_name,
            department_name=department_name,
            doctor_name=doctor_name,
            created_by_name=created_by_name
        ))
    
    return enriched_assignments


@router.post("/", response_model=AssignmentResponse)
async def create_assignment(
    assignment_data: AssignmentCreate,
    current_user: Utilisateur = Depends(get_current_user)
):
    """Créer une nouvelle assignation patient-médecin."""
    
    # Seuls les médecins et admins peuvent créer des assignations
    if current_user.role not in ["medecin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les médecins et admins peuvent créer des assignations"
        )
    
    # Vérifier que le patient existe
    patient = await Utilisateur.get(assignment_data.patient_id)
    if not patient or patient.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    # Vérifier que le médecin existe
    doctor = await Utilisateur.get(assignment_data.doctor_id)
    if not doctor or doctor.role != "medecin":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médecin non trouvé"
        )
    
    # Vérifier que le département existe
    department = await Department.get(assignment_data.department_id)
    if not department or not department.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Département non trouvé ou inactif"
        )
    
    # Vérifier que le médecin appartient au département
    if doctor.department_id != assignment_data.department_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le médecin n'appartient pas au département spécifié"
        )
    
    # Vérifier qu'il n'y a pas déjà une assignation active pour ce patient
    existing_assignment = await Assignment.find_one({
        "patient_id": assignment_data.patient_id,
        "status": "active"
    })
    
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le patient a déjà une assignation active"
        )
    
    # Créer l'assignation
    assignment = Assignment(
        patient_id=assignment_data.patient_id,
        department_id=assignment_data.department_id,
        doctor_id=assignment_data.doctor_id,
        referral_id=assignment_data.referral_id,
        notes=assignment_data.notes,
        created_by=str(current_user.id)
    )
    
    await assignment.insert()
    
    # Mettre à jour le patient avec l'assignation
    patient.current_assignment_id = str(assignment.id)
    await patient.save()
    
    return AssignmentResponse(
        id=str(assignment.id),
        patient_id=assignment.patient_id,
        department_id=assignment.department_id,
        doctor_id=assignment.doctor_id,
        referral_id=assignment.referral_id,
        status=assignment.status,
        notes=assignment.notes,
        start_at=assignment.start_at,
        end_at=assignment.end_at,
        created_by=assignment.created_by,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
        patient_name=patient.username,
        department_name=department.name,
        doctor_name=doctor.username,
        created_by_name=current_user.username
    )


@router.patch("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: str,
    assignment_data: AssignmentUpdate,
    current_user: Utilisateur = Depends(get_current_user)
):
    """Mettre à jour une assignation (terminer, suspendre, etc.)."""
    
    assignment = await Assignment.get(assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignation non trouvée"
        )
    
    # Vérifier les permissions
    if current_user.role == "medecin":
        # Médecin : peut modifier ses propres assignations
        if assignment.doctor_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez modifier que vos propres assignations"
            )
    elif current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les médecins et admins peuvent modifier les assignations"
        )
    
    # Mettre à jour les champs
    if assignment_data.status is not None:
        assignment.status = assignment_data.status
        
        # Si l'assignation se termine, mettre à jour la date de fin
        if assignment_data.status == "ended":
            assignment.end_at = datetime.utcnow()
            
            # Retirer l'assignation du patient
            patient = await Utilisateur.get(assignment.patient_id)
            if patient:
                patient.current_assignment_id = None
                await patient.save()
    
    if assignment_data.notes is not None:
        assignment.notes = assignment_data.notes
    
    if assignment_data.end_at is not None:
        assignment.end_at = assignment_data.end_at
    
    assignment.updated_at = datetime.utcnow()
    await assignment.save()
    
    # Enrichir la réponse
    patient = await Utilisateur.get(assignment.patient_id)
    department = await Department.get(assignment.department_id)
    doctor = await Utilisateur.get(assignment.doctor_id)
    
    return AssignmentResponse(
        id=str(assignment.id),
        patient_id=assignment.patient_id,
        department_id=assignment.department_id,
        doctor_id=assignment.doctor_id,
        referral_id=assignment.referral_id,
        status=assignment.status,
        notes=assignment.notes,
        start_at=assignment.start_at,
        end_at=assignment.end_at,
        created_by=assignment.created_by,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
        patient_name=patient.username if patient else "Inconnu",
        department_name=department.name if department else "Inconnu",
        doctor_name=doctor.username if doctor else "Inconnu",
        created_by_name=current_user.username
    )


@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: str,
    current_user: Utilisateur = Depends(require_role("admin"))
):
    """Supprimer une assignation (admin uniquement)."""
    
    assignment = await Assignment.get(assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignation non trouvée"
        )
    
    # Retirer l'assignation du patient si elle est active
    if assignment.status == "active":
        patient = await Utilisateur.get(assignment.patient_id)
        if patient and patient.current_assignment_id == str(assignment.id):
            patient.current_assignment_id = None
            await patient.save()
    
    await assignment.delete()
    
    return {"message": "Assignation supprimée avec succès"}
