"""Routeur pour la gestion des assignations patient-médecin.
Accessible uniquement aux techniciens médicaux.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from pydantic import BaseModel
from backend.models.utilisateur import Utilisateur, Role
from backend.services.ia_assignation import ia_assignation_service
from backend.dependencies.auth import get_current_user, verifier_roles
from backend.db import get_client, MONGO_DB_NAME
from bson import ObjectId
from datetime import datetime

router = APIRouter()

# Schémas Pydantic
class AssignationRequest(BaseModel):
    patient_id: str
    medecin_id: Optional[str] = None  # Si None, utilise l'IA
    department_id: Optional[str] = None

class AssignationResponse(BaseModel):
    id: str
    patient_id: str
    patient_nom: str
    medecin_id: str
    medecin_nom: str
    date_assignation: str
    type: str
    statut: str

class PatientSansAssignation(BaseModel):
    id: str
    username: str
    email: str
    department_id: Optional[str]
    date_inscription: str

class MedecinDisponible(BaseModel):
    id: str
    username: str
    email: str
    department_id: str
    nb_patients: int
    charge_travail: str

@router.get("/patients-sans-assignation", response_model=List[PatientSansAssignation])
async def get_patients_sans_assignation(current_user=Depends(verifier_roles([Role.technicien]))):
    """Récupère la liste des patients sans médecin assigné."""
    client = get_client()
    db = client[MONGO_DB_NAME]
    
    # Trouver les patients sans médecin assigné
    patients_cursor = db.utilisateurs.find({
        "role": "patient",
        "$or": [
            {"medecin_ids": {"$exists": False}},
            {"medecin_ids": {"$size": 0}},
            {"medecin_ids": None}
        ]
    })
    
    patients = []
    async for patient in patients_cursor:
        patients.append(PatientSansAssignation(
            id=str(patient["_id"]),
            username=patient["username"],
            email=patient["email"],
            department_id=patient.get("department_id"),
            date_inscription=patient.get("created_at", datetime.utcnow()).isoformat() if isinstance(patient.get("created_at"), datetime) else str(patient.get("created_at", ""))
        ))
    
    return patients

@router.get("/medecins-disponibles", response_model=List[MedecinDisponible])
async def get_medecins_disponibles(department_id: Optional[str] = None, current_user=Depends(verifier_roles([Role.technicien]))):
    """Récupère la liste des médecins disponibles avec leur charge de travail."""
    client = get_client()
    db = client[MONGO_DB_NAME]
    
    # Construire la requête
    query = {"role": "medecin", "statut": "actif"}
    if department_id:
        query["department_id"] = department_id
    
    medecins_cursor = db.utilisateurs.find(query)
    medecins = []
    
    async for medecin in medecins_cursor:
        # Compter le nombre de patients assignés
        nb_patients = await db.utilisateurs.count_documents({
            "role": "patient",
            "medecin_ids": str(medecin["_id"])
        })
        
        # Déterminer la charge de travail
        if nb_patients == 0:
            charge = "Libre"
        elif nb_patients <= 3:
            charge = "Faible"
        elif nb_patients <= 7:
            charge = "Modérée"
        elif nb_patients <= 10:
            charge = "Élevée"
        else:
            charge = "Saturé"
        
        medecins.append(MedecinDisponible(
            id=str(medecin["_id"]),
            username=medecin["username"],
            email=medecin["email"],
            department_id=medecin.get("department_id", ""),
            nb_patients=nb_patients,
            charge_travail=charge
        ))
    
    return sorted(medecins, key=lambda m: m.nb_patients)

@router.post("/assigner", response_model=dict)
async def assigner_patient_medecin(
    assignation: AssignationRequest,
    current_user=Depends(verifier_roles([Role.technicien]))
):
    """Assigne un patient à un médecin (manuellement ou via IA)."""
    client = get_client()
    db = client[MONGO_DB_NAME]
    
    # Vérifier que le patient existe et n'est pas déjà assigné
    patient = await db.utilisateurs.find_one({"_id": ObjectId(assignation.patient_id), "role": "patient"})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    
    if patient.get("medecin_ids") and len(patient.get("medecin_ids", [])) > 0:
        raise HTTPException(status_code=400, detail="Ce patient est déjà assigné à un médecin")
    
    # Si medecin_id est fourni, assignation manuelle
    if assignation.medecin_id:
        # Vérifier que le médecin existe
        medecin = await db.utilisateurs.find_one({"_id": ObjectId(assignation.medecin_id), "role": "medecin"})
        if not medecin:
            raise HTTPException(status_code=404, detail="Médecin introuvable")
        
        # Effectuer l'assignation manuelle
        await db.utilisateurs.update_one(
            {"_id": ObjectId(assignation.patient_id)},
            {"$set": {"medecin_ids": [assignation.medecin_id]}}
        )
        
        await db.utilisateurs.update_one(
            {"_id": ObjectId(assignation.medecin_id)},
            {"$addToSet": {"patient_ids": assignation.patient_id}}
        )
        
        # Log de l'assignation
        await db.assignation_logs.insert_one({
            "patient_id": assignation.patient_id,
            "medecin_id": assignation.medecin_id,
            "type": "manuelle_technicien",
            "technicien_id": str(current_user.id),
            "date": datetime.utcnow(),
            "statut": "active"
        })
        
        return {
            "success": True,
            "message": f"Patient {patient['username']} assigné manuellement au Dr. {medecin['username']}",
            "type": "manuelle",
            "medecin_id": assignation.medecin_id
        }
    
    # Sinon, utiliser l'IA pour l'assignation
    else:
        medecin_id = await ia_assignation_service.assigner_medecin_automatique(
            assignation.patient_id, 
            assignation.department_id
        )
        
        if not medecin_id:
            raise HTTPException(status_code=400, detail="Aucun médecin disponible trouvé par l'IA")
        
        # Récupérer le nom du médecin assigné
        medecin = await db.utilisateurs.find_one({"_id": ObjectId(medecin_id)})
        
        # Effectuer l'assignation effective (comme la branche manuelle)
        await db.utilisateurs.update_one(
            {"_id": ObjectId(assignation.patient_id)},
            {"$set": {"medecin_ids": [medecin_id]}}
        )
        await db.utilisateurs.update_one(
            {"_id": ObjectId(medecin_id)},
            {"$addToSet": {"patient_ids": assignation.patient_id}}
        )

        # Log de l'assignation IA validée par technicien
        await db.assignation_logs.update_one(
            {"patient_id": assignation.patient_id, "medecin_id": medecin_id},
            {"$set": {"technicien_validation": str(current_user.id), "type": "ia_validee_technicien"}},
            upsert=True
        )
        
        return {
            "success": True,
            "message": f"Patient {patient['username']} assigné par l'IA au Dr. {medecin['username']}",
            "type": "ia",
            "medecin_id": medecin_id,
            "medecin_nom": medecin['username']
        }

@router.get("/historique", response_model=List[AssignationResponse])
async def get_historique_assignations(current_user=Depends(verifier_roles([Role.technicien]))):
    """Récupère l'historique des assignations."""
    client = get_client()
    db = client[MONGO_DB_NAME]
    
    # Récupérer les logs d'assignation
    logs_cursor = db.assignation_logs.find({"statut": "active"}).sort("date", -1).limit(50)
    
    assignations = []
    async for log in logs_cursor:
        # Récupérer les infos patient et médecin
        patient = await db.utilisateurs.find_one({"_id": ObjectId(log["patient_id"])})
        medecin = await db.utilisateurs.find_one({"_id": ObjectId(log["medecin_id"])})
        
        if patient and medecin:
            assignations.append(AssignationResponse(
                id=str(log["_id"]),
                patient_id=log["patient_id"],
                patient_nom=patient["username"],
                medecin_id=log["medecin_id"],
                medecin_nom=medecin["username"],
                date_assignation=log["date"].isoformat() if isinstance(log["date"], datetime) else str(log["date"]),
                type=log.get("type", "inconnue"),
                statut=log["statut"]
            ))
    
    return assignations

@router.delete("/desassigner/{patient_id}")
async def desassigner_patient(patient_id: str, current_user=Depends(verifier_roles([Role.technicien]))):
    """Désassigne un patient de son médecin."""
    client = get_client()
    db = client[MONGO_DB_NAME]
    
    # Récupérer le patient
    patient = await db.utilisateurs.find_one({"_id": ObjectId(patient_id), "role": "patient"})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    
    medecin_ids = patient.get("medecin_ids", [])
    if not medecin_ids:
        raise HTTPException(status_code=400, detail="Ce patient n'est assigné à aucun médecin")
    
    # Désassigner du côté patient
    await db.utilisateurs.update_one(
        {"_id": ObjectId(patient_id)},
        {"$unset": {"medecin_ids": ""}}
    )
    
    # Désassigner du côté médecin
    for medecin_id in medecin_ids:
        await db.utilisateurs.update_one(
            {"_id": ObjectId(medecin_id)},
            {"$pull": {"patient_ids": patient_id}}
        )
    
    # Marquer les logs comme inactifs
    await db.assignation_logs.update_many(
        {"patient_id": patient_id, "statut": "active"},
        {"$set": {"statut": "desassigne", "date_desassignation": datetime.utcnow()}}
    )
    
    return {"success": True, "message": f"Patient {patient['username']} désassigné avec succès"}
