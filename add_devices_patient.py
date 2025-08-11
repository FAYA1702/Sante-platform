#!/usr/bin/env python3
"""
Ajouter des appareils médicaux pour un patient
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def add_devices_for_patient():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== AJOUT APPAREILS POUR PATIENT ===")
    
    # Trouver le patient "fall"
    patient = await db.utilisateurs.find_one({"username": "fall", "role": "patient"})
    
    if not patient:
        print("Patient 'fall' non trouvé!")
        return
    
    patient_id = str(patient["_id"])
    print(f"Patient trouvé: {patient['username']} ({patient_id})")
    
    # Créer des appareils médicaux pour ce patient
    appareils = [
        {
            "nom": "Oxymètre de pouls",
            "type": "oxymetre",
            "modele": "PulseOx Pro 2024",
            "numero_serie": f"POX-{patient_id[:8]}-001",
            "user_id": patient_id,
            "statut": "actif",
            "date_installation": datetime.utcnow(),
            "derniere_maintenance": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "nom": "Tensiomètre connecté",
            "type": "tensiometre",
            "modele": "BloodPress Smart",
            "numero_serie": f"BP-{patient_id[:8]}-002",
            "user_id": patient_id,
            "statut": "actif",
            "date_installation": datetime.utcnow(),
            "derniere_maintenance": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "nom": "Moniteur cardiaque",
            "type": "ecg",
            "modele": "CardioWatch 3000",
            "numero_serie": f"ECG-{patient_id[:8]}-003",
            "user_id": patient_id,
            "statut": "actif",
            "date_installation": datetime.utcnow(),
            "derniere_maintenance": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
    ]
    
    # Insérer les appareils
    result = await db.appareils.insert_many(appareils)
    print(f"Appareils créés: {len(result.inserted_ids)}")
    
    # Afficher les appareils créés
    for i, appareil in enumerate(appareils):
        print(f"  {i+1}. {appareil['nom']} ({appareil['type']})")
        print(f"     Série: {appareil['numero_serie']}")
    
    # Vérifier le résultat
    appareils_count = await db.appareils.count_documents({"user_id": patient_id})
    print(f"\nTotal appareils pour patient '{patient['username']}': {appareils_count}")
    
    client.close()
    print("Ajout terminé!")

if __name__ == "__main__":
    asyncio.run(add_devices_for_patient())
