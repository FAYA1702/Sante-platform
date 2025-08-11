#!/usr/bin/env python3
"""Script pour vérifier les assignations patient-médecin dans MongoDB."""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from backend.models.utilisateur import Utilisateur
from backend.db import MONGO_URI, MONGO_DB_NAME

async def check_assignments():
    """Vérifie les assignations entre fall (patient) et kodia (médecin)."""
    client = AsyncIOMotorClient(MONGO_URI)
    await init_beanie(database=client[MONGO_DB_NAME], document_models=[Utilisateur])
    
    # Récupérer fall et kodia
    fall = await Utilisateur.find_one({"username": "fall"})
    kodia = await Utilisateur.find_one({"username": "kodia"})
    
    print("=== VERIFICATION DES ASSIGNATIONS ===")
    
    if fall:
        print(f"\nPATIENT: {fall.username}")
        print(f"   Role: {fall.role}")
        print(f"   Department ID: {fall.department_id}")
        print(f"   Medecins assignes: {fall.medecin_ids}")
    else:
        print("\nPatient 'fall' non trouve")
    
    if kodia:
        print(f"\nMEDECIN: {kodia.username}")
        print(f"   Role: {kodia.role}")
        print(f"   Department ID: {kodia.department_id}")
        print(f"   Patients assignes: {kodia.patient_ids}")
    else:
        print("\nMedecin 'kodia' non trouve")
    
    # Vérifier l'assignation bidirectionnelle
    if fall and kodia:
        fall_id = str(fall.id)
        kodia_id = str(kodia.id)
        
        print(f"\nVERIFICATION ASSIGNATION:")
        print(f"   fall.medecin_ids contient kodia? {kodia_id in fall.medecin_ids}")
        print(f"   kodia.patient_ids contient fall? {fall_id in kodia.patient_ids}")
        
        if kodia_id in fall.medecin_ids and fall_id in kodia.patient_ids:
            print("   OK: Assignation bidirectionnelle")
        else:
            print("   PROBLEME: Assignation manquante ou incomplete")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_assignments())
