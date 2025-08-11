"""Routeur FastAPI pour la gestion des départements/services médicaux.
Tous les commentaires sont rédigés en français.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from ..models import Department
from ..schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from ..dependencies.auth import get_current_user, require_role
from ..models.utilisateur import Utilisateur

router = APIRouter(prefix="/departments", tags=["Départements"])


@router.get("/", response_model=List[DepartmentResponse])
async def get_departments(
    current_user: Utilisateur = Depends(get_current_user)
):
    """Récupérer la liste de tous les départements actifs."""
    departments = await Department.find({"is_active": True}).to_list()
    return [
        DepartmentResponse(
            id=str(dept.id),
            name=dept.name,
            code=dept.code,
            description=dept.description,
            is_active=dept.is_active,
            created_at=dept.created_at,
            updated_at=dept.updated_at
        )
        for dept in departments
    ]


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: str,
    current_user: Utilisateur = Depends(get_current_user)
):
    """Récupérer un département par son ID."""
    department = await Department.get(department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Département non trouvé"
        )
    
    return DepartmentResponse(
        id=str(department.id),
        name=department.name,
        code=department.code,
        description=department.description,
        is_active=department.is_active,
        created_at=department.created_at,
        updated_at=department.updated_at
    )


@router.post("/", response_model=DepartmentResponse)
async def create_department(
    department_data: DepartmentCreate,
    current_user: Utilisateur = Depends(require_role("admin"))
):
    """Créer un nouveau département (admin uniquement)."""
    # Vérifier l'unicité du nom et du code
    existing_name = await Department.find_one({"name": department_data.name})
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un département avec ce nom existe déjà"
        )
    
    existing_code = await Department.find_one({"code": department_data.code})
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un département avec ce code existe déjà"
        )
    
    # Créer le département
    department = Department(**department_data.dict())
    await department.insert()
    
    return DepartmentResponse(
        id=str(department.id),
        name=department.name,
        code=department.code,
        description=department.description,
        is_active=department.is_active,
        created_at=department.created_at,
        updated_at=department.updated_at
    )


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    department_data: DepartmentUpdate,
    current_user: Utilisateur = Depends(require_role("admin"))
):
    """Mettre à jour un département (admin uniquement)."""
    department = await Department.get(department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Département non trouvé"
        )
    
    # Mettre à jour les champs fournis
    update_data = department_data.dict(exclude_unset=True)
    if update_data:
        for field, value in update_data.items():
            setattr(department, field, value)
        
        from datetime import datetime
        department.updated_at = datetime.utcnow()
        await department.save()
    
    return DepartmentResponse(
        id=str(department.id),
        name=department.name,
        code=department.code,
        description=department.description,
        is_active=department.is_active,
        created_at=department.created_at,
        updated_at=department.updated_at
    )


@router.delete("/{department_id}")
async def delete_department(
    department_id: str,
    current_user: Utilisateur = Depends(require_role("admin"))
):
    """Supprimer (désactiver) un département (admin uniquement)."""
    department = await Department.get(department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Département non trouvé"
        )
    
    # Désactiver plutôt que supprimer (soft delete)
    department.is_active = False
    from datetime import datetime
    department.updated_at = datetime.utcnow()
    await department.save()
    
    return {"message": "Département désactivé avec succès"}
