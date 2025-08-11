#!/usr/bin/env python3
"""Script pour vérifier les identifiants du médecin faye dans MongoDB.
Tous les commentaires sont rédigés en français.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt

# Configuration MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sante_db")

async def check_doctor_credentials():
    """Vérifie les identifiants du médecin faye."""
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    
    # Rechercher le médecin faye
    medecin = await db.utilisateurs.find_one({"username": "faye"})
    if not medecin:
        print("Medecin 'faye' non trouve dans la base")
        return
    
    print(f"Medecin trouve: {medecin['username']}")
    print(f"Email: {medecin.get('email', 'N/A')}")
    print(f"Role: {medecin.get('role', 'N/A')}")
    print(f"Department ID: {medecin.get('department_id', 'N/A')}")
    
    # Vérifier le hash du mot de passe
    hash_password = medecin.get('mot_de_passe_hache', '')
    print(f"Hash mot de passe: {hash_password[:50]}...")
    
    # Tester différents mots de passe possibles
    test_passwords = ['faye123', 'motdepasse123', 'password', 'faye', '123456']
    
    for pwd in test_passwords:
        try:
            if bcrypt.checkpw(pwd.encode('utf-8'), hash_password.encode('utf-8')):
                print(f"MOT DE PASSE CORRECT: '{pwd}'")
                break
        except Exception as e:
            print(f"Erreur test mot de passe '{pwd}': {e}")
    else:
        print("Aucun mot de passe teste ne correspond")
    
    # Fermer la connexion
    client.close()
    print("Verification terminee")

if __name__ == "__main__":
    asyncio.run(check_doctor_credentials())
