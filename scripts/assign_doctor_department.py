#!/usr/bin/env python3
"""Script pour assigner un médecin à un département.
Tous les commentaires sont rédigés en français.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Configuration MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sante_db")

async def assign_doctor_to_department():
    """Assigne un médecin au département de Cardiologie."""
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    
    # Trouver un médecin existant
    medecin = await db.utilisateurs.find_one({"role": "medecin"})
    if not medecin:
        print("Aucun medecin trouve dans la base")
        return
    
    # Trouver le département Cardiologie
    cardio_dept = await db.departments.find_one({"code": "CARDIO"})
    if not cardio_dept:
        print("Departement CARDIO non trouve")
        return
    
    # Assigner le médecin au département
    result = await db.utilisateurs.update_one(
        {"_id": medecin["_id"]},
        {"$set": {"department_id": str(cardio_dept["_id"])}}
    )
    
    if result.modified_count > 0:
        print(f"Medecin {medecin['username']} assigne au departement Cardiologie")
        print(f"Department ID: {cardio_dept['_id']}")
    else:
        print("Erreur lors de l'assignation")
    
    # Vérifier l'assignation
    updated_medecin = await db.utilisateurs.find_one({"_id": medecin["_id"]})
    if updated_medecin.get("department_id"):
        print(f"Verification: department_id = {updated_medecin['department_id']}")
    
    # Fermer la connexion
    client.close()
    print("Assignation medecin-departement terminee !")

if __name__ == "__main__":
    asyncio.run(assign_doctor_to_department())
