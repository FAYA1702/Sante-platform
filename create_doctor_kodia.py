#!/usr/bin/env python3
"""
Script pour créer le médecin "kodia" et tester le système d'assignation
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt

async def create_doctor_kodia():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== CRÉATION DU MÉDECIN 'kodia' ===")
    
    # Vérifier si le médecin existe déjà
    existing_doctor = await db.utilisateurs.find_one({"username": "kodia"})
    if existing_doctor:
        print("✅ Le médecin 'kodia' existe déjà")
        print(f"   Email: {existing_doctor.get('email', 'N/A')}")
        print(f"   Role: {existing_doctor.get('role', 'N/A')}")
        return str(existing_doctor["_id"])
    
    # Créer le médecin kodia
    password = "kodia123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    doctor_data = {
        "email": "kodia@sante.com",
        "username": "kodia",
        "mot_de_passe_hache": hashed_password,
        "role": "medecin",
        "medecin_ids": [],  # Vide pour un médecin
        "patient_ids": [],  # Liste des patients assignés
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True
    }
    
    result = await db.utilisateurs.insert_one(doctor_data)
    doctor_id = str(result.inserted_id)
    
    print("✅ Médecin 'kodia' créé avec succès!")
    print(f"   ID: {doctor_id}")
    print(f"   Email: kodia@sante.com")
    print(f"   Username: kodia")
    print(f"   Password: kodia123")
    print(f"   Role: medecin")
    
    client.close()
    return doctor_id

async def test_assignation_demo():
    """Démonstration complète du système d'assignation"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("\n=== DÉMONSTRATION ASSIGNATION PATIENT-MÉDECIN ===")
    
    # 1. Récupérer le patient "fall"
    patient = await db.utilisateurs.find_one({"username": "fall", "role": "patient"})
    if not patient:
        print("❌ Patient 'fall' non trouvé")
        return
    
    # 2. Récupérer le médecin "kodia"
    medecin = await db.utilisateurs.find_one({"username": "kodia", "role": "medecin"})
    if not medecin:
        print("❌ Médecin 'kodia' non trouvé")
        return
    
    patient_id = str(patient["_id"])
    medecin_id = str(medecin["_id"])
    
    print(f"Patient: {patient['username']} (ID: {patient_id})")
    print(f"Médecin: Dr. {medecin['username']} (ID: {medecin_id})")
    
    # 3. Vérifier l'assignation actuelle
    print(f"\nAvant assignation:")
    print(f"  Patient 'fall' - médecins assignés: {patient.get('medecin_ids', [])}")
    print(f"  Médecin 'kodia' - patients assignés: {medecin.get('patient_ids', [])}")
    
    # 4. Effectuer l'assignation si elle n'existe pas
    if medecin_id not in patient.get('medecin_ids', []):
        # Assigner côté patient
        await db.utilisateurs.update_one(
            {"_id": patient["_id"]},
            {"$addToSet": {"medecin_ids": medecin_id}}
        )
        
        # Assigner côté médecin
        await db.utilisateurs.update_one(
            {"_id": medecin["_id"]},
            {"$addToSet": {"patient_ids": patient_id}}
        )
        
        print(f"\n✅ Assignation effectuée!")
    else:
        print(f"\n✅ Assignation déjà existante!")
    
    # 5. Vérifier l'assignation finale
    patient_updated = await db.utilisateurs.find_one({"_id": patient["_id"]})
    medecin_updated = await db.utilisateurs.find_one({"_id": medecin["_id"]})
    
    print(f"\nAprès assignation:")
    print(f"  Patient 'fall' - médecins assignés: {patient_updated.get('medecin_ids', [])}")
    print(f"  Médecin 'kodia' - patients assignés: {medecin_updated.get('patient_ids', [])}")
    
    client.close()

async def main():
    print("CONFIGURATION DU SYSTEME D'ASSIGNATION PATIENT-MEDECIN")
    
    # Créer le médecin kodia
    doctor_id = await create_doctor_kodia()
    
    # Démonstration de l'assignation
    await test_assignation_demo()
    
    print("\nINSTRUCTIONS POUR UTILISER LE SYSTEME:")
    print("1. Redémarrez le backend Docker: docker-compose restart backend")
    print("2. Connectez-vous en tant que patient 'fall' (mot de passe: 123456)")
    print("3. Utilisez les nouveaux endpoints d'assignation:")
    print("   - GET /assignation/tous-medecins (voir tous les médecins)")
    print("   - POST /assignation/demander-assignation (s'assigner à un médecin)")
    print("   - GET /assignation/mes-medecins (voir ses médecins)")
    print("4. Connectez-vous en tant que médecin 'kodia' (mot de passe: kodia123)")
    print("   - GET /assignation/mes-patients (voir ses patients)")
    
    print("\nFONCTIONNALITES DISPONIBLES:")
    print("✅ Création automatique des relations patient-médecin")
    print("✅ API complète pour la gestion des assignations")
    print("✅ Sécurité RGPD respectée (filtrage par utilisateur)")
    print("✅ Interface pour patients et médecins")
    print("✅ Gestion administrative des assignations")

if __name__ == "__main__":
    asyncio.run(main())
