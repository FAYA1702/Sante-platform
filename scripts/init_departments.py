#!/usr/bin/env python3
"""Script pour initialiser les départements médicaux dans MongoDB.
Tous les commentaires sont rédigés en français.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Configuration MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sante_db")

async def init_departments():
    """Initialise les départements médicaux de base."""
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    
    # Départements de base
    departments = [
        {
            "name": "Médecine Générale",
            "code": "GENERAL",
            "description": "Médecine générale et soins primaires",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Cardiologie",
            "code": "CARDIO",
            "description": "Spécialité des maladies cardiovasculaires",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Pneumologie",
            "code": "PNEUMO",
            "description": "Spécialité des maladies respiratoires",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Supprimer les anciens départements
    await db.departments.delete_many({})
    print("Anciens departements supprimes")
    
    # Insérer les nouveaux départements
    result = await db.departments.insert_many(departments)
    print(f"{len(result.inserted_ids)} departements crees")
    
    # Afficher les départements créés
    async for dept in db.departments.find():
        print(f"   - {dept['name']} ({dept['code']})")
    
    # Fermer la connexion
    client.close()
    print("Departements medicaux initialises avec succes !")

if __name__ == "__main__":
    asyncio.run(init_departments())
