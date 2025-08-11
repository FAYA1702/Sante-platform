#!/usr/bin/env python3
"""
Script simple pour configurer le systeme d'assignation patient-medecin
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt

async def create_doctor_kodia():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== CREATION DU MEDECIN 'kodia' ===")
    
    # Verifier si le medecin existe deja
    existing_doctor = await db.utilisateurs.find_one({"username": "kodia"})
    if existing_doctor:
        print("Le medecin 'kodia' existe deja")
        print(f"   Email: {existing_doctor.get('email', 'N/A')}")
        print(f"   Role: {existing_doctor.get('role', 'N/A')}")
        client.close()
        return str(existing_doctor["_id"])
    
    # Creer le medecin kodia
    password = "kodia123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    doctor_data = {
        "email": "kodia@sante.com",
        "username": "kodia",
        "mot_de_passe_hache": hashed_password,
        "role": "medecin",
        "medecin_ids": [],  # Vide pour un medecin
        "patient_ids": [],  # Liste des patients assignes
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True
    }
    
    result = await db.utilisateurs.insert_one(doctor_data)
    doctor_id = str(result.inserted_id)
    
    print("Medecin 'kodia' cree avec succes!")
    print(f"   ID: {doctor_id}")
    print(f"   Email: kodia@sante.com")
    print(f"   Username: kodia")
    print(f"   Password: kodia123")
    print(f"   Role: medecin")
    
    client.close()
    return doctor_id

async def test_assignation_demo():
    """Demonstration complete du systeme d'assignation"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("\n=== DEMONSTRATION ASSIGNATION PATIENT-MEDECIN ===")
    
    # 1. Recuperer le patient "fall"
    patient = await db.utilisateurs.find_one({"username": "fall", "role": "patient"})
    if not patient:
        print("Patient 'fall' non trouve")
        client.close()
        return
    
    # 2. Recuperer le medecin "kodia"
    medecin = await db.utilisateurs.find_one({"username": "kodia", "role": "medecin"})
    if not medecin:
        print("Medecin 'kodia' non trouve")
        client.close()
        return
    
    patient_id = str(patient["_id"])
    medecin_id = str(medecin["_id"])
    
    print(f"Patient: {patient['username']} (ID: {patient_id})")
    print(f"Medecin: Dr. {medecin['username']} (ID: {medecin_id})")
    
    # 3. Verifier l'assignation actuelle
    print(f"\nAvant assignation:")
    print(f"  Patient 'fall' - medecins assignes: {patient.get('medecin_ids', [])}")
    print(f"  Medecin 'kodia' - patients assignes: {medecin.get('patient_ids', [])}")
    
    # 4. Effectuer l'assignation si elle n'existe pas
    if medecin_id not in patient.get('medecin_ids', []):
        # Assigner cote patient
        await db.utilisateurs.update_one(
            {"_id": patient["_id"]},
            {"$addToSet": {"medecin_ids": medecin_id}}
        )
        
        # Assigner cote medecin
        await db.utilisateurs.update_one(
            {"_id": medecin["_id"]},
            {"$addToSet": {"patient_ids": patient_id}}
        )
        
        print(f"\nAssignation effectuee!")
    else:
        print(f"\nAssignation deja existante!")
    
    # 5. Verifier l'assignation finale
    patient_updated = await db.utilisateurs.find_one({"_id": patient["_id"]})
    medecin_updated = await db.utilisateurs.find_one({"_id": medecin["_id"]})
    
    print(f"\nApres assignation:")
    print(f"  Patient 'fall' - medecins assignes: {patient_updated.get('medecin_ids', [])}")
    print(f"  Medecin 'kodia' - patients assignes: {medecin_updated.get('patient_ids', [])}")
    
    client.close()

async def main():
    print("CONFIGURATION DU SYSTEME D'ASSIGNATION PATIENT-MEDECIN")
    
    # Creer le medecin kodia
    doctor_id = await create_doctor_kodia()
    
    # Demonstration de l'assignation
    await test_assignation_demo()
    
    print("\nINSTRUCTIONS POUR UTILISER LE SYSTEME:")
    print("1. Redemarrez le backend Docker: docker-compose restart backend")
    print("2. Connectez-vous en tant que patient 'fall' (mot de passe: 123456)")
    print("3. Utilisez les nouveaux endpoints d'assignation:")
    print("   - GET /assignation/tous-medecins (voir tous les medecins)")
    print("   - POST /assignation/demander-assignation (s'assigner a un medecin)")
    print("   - GET /assignation/mes-medecins (voir ses medecins)")
    print("4. Connectez-vous en tant que medecin 'kodia' (mot de passe: kodia123)")
    print("   - GET /assignation/mes-patients (voir ses patients)")
    
    print("\nFONCTIONNALITES DISPONIBLES:")
    print("- Creation automatique des relations patient-medecin")
    print("- API complete pour la gestion des assignations")
    print("- Securite RGPD respectee (filtrage par utilisateur)")
    print("- Interface pour patients et medecins")
    print("- Gestion administrative des assignations")

if __name__ == "__main__":
    asyncio.run(main())
