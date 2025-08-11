#!/usr/bin/env python3
"""
Réinitialiser le mot de passe du médecin talla
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import bcrypt

async def reset_password():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== REINITIALISATION MOT DE PASSE TALLA ===")
    
    # Trouver le médecin talla
    talla = await db.utilisateurs.find_one({"username": "talla", "role": "medecin"})
    
    if not talla:
        print("Médecin talla non trouvé!")
        return
    
    print(f"Médecin talla trouvé: {talla['_id']}")
    print(f"Email: {talla.get('email', 'N/A')}")
    
    # Nouveau mot de passe simple
    new_password = "talla123"
    
    # Hacher le mot de passe
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    # Mettre à jour en base
    result = await db.utilisateurs.update_one(
        {"_id": talla["_id"]},
        {"$set": {"mot_de_passe_hache": hashed}}
    )
    
    print(f"Mot de passe mis à jour: {result.modified_count} document(s)")
    print(f"Nouveau mot de passe: {new_password}")
    
    # Vérifier les assignations
    print(f"\nPatients assignés: {talla.get('patient_ids', [])}")
    
    client.close()
    print("Réinitialisation terminée!")

if __name__ == "__main__":
    asyncio.run(reset_password())
