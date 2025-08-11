#!/usr/bin/env python3
"""
Vérifier les informations de connexion du patient "fall"
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt

async def check_patient_password():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== VERIFICATION PATIENT 'fall' ===")
    
    # Trouver le patient "fall"
    patient = await db.utilisateurs.find_one({"username": "fall", "role": "patient"})
    
    if not patient:
        print("Patient 'fall' non trouvé!")
        return
    
    print(f"Patient trouvé: {patient['username']}")
    print(f"Email: {patient.get('email', 'N/A')}")
    print(f"Role: {patient.get('role', 'N/A')}")
    print(f"Créé le: {patient.get('created_at', 'N/A')}")
    
    # Vérifier le hash du mot de passe
    hash_password = patient.get('mot_de_passe_hache', '')
    print(f"Hash mot de passe: {hash_password[:50]}...")
    
    # Tester différents mots de passe possibles
    test_passwords = [
        "fall123",
        "fall",
        "password",
        "123456",
        "fall@17.com",
        "admin123"
    ]
    
    print("\nTest des mots de passe possibles:")
    for pwd in test_passwords:
        try:
            if bcrypt.checkpw(pwd.encode('utf-8'), hash_password.encode('utf-8')):
                print(f"TROUVE! Mot de passe: '{pwd}'")
                break
            else:
                print(f"'{pwd}' - incorrect")
        except Exception as e:
            print(f"'{pwd}' - erreur: {e}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_patient_password())
