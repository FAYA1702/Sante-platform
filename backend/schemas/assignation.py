"""
Schémas Pydantic pour la gestion des assignations patient-médecin.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AssignationRequest(BaseModel):
    """Requête d'assignation patient-médecin."""
    medecin_id: Optional[str] = Field(None, description="ID du médecin (pour demande patient)")
    patient_id: Optional[str] = Field(None, description="ID du patient (pour acceptation médecin)")


class AssignationResponse(BaseModel):
    """Réponse d'une opération d'assignation."""
    success: bool = Field(..., description="Succès de l'opération")
    message: str = Field(..., description="Message de confirmation")


class MedecinInfo(BaseModel):
    """Informations d'un médecin."""
    id: str = Field(..., description="ID du médecin")
    username: str = Field(..., description="Nom d'utilisateur")
    email: str = Field(..., description="Email")
    specialite: str = Field(default="Médecin généraliste", description="Spécialité médicale")
    nb_patients: Optional[int] = Field(None, description="Nombre de patients assignés")


class PatientInfo(BaseModel):
    """Informations d'un patient."""
    id: str = Field(..., description="ID du patient")
    username: str = Field(..., description="Nom d'utilisateur")
    email: str = Field(..., description="Email")
    date_assignation: str = Field(..., description="Date d'assignation")


class ListeMedecins(BaseModel):
    """Liste des médecins."""
    medecins: List[MedecinInfo] = Field(default=[], description="Liste des médecins")


class ListePatients(BaseModel):
    """Liste des patients."""
    patients: List[PatientInfo] = Field(default=[], description="Liste des patients")


class StatistiquesAssignation(BaseModel):
    """Statistiques des assignations."""
    total_medecins: int = Field(..., description="Nombre total de médecins")
    total_patients: int = Field(..., description="Nombre total de patients")
    total_assignations: int = Field(..., description="Nombre total d'assignations")
    medecins_sans_patients: int = Field(..., description="Médecins sans patients")
    patients_sans_medecins: int = Field(..., description="Patients sans médecins")
