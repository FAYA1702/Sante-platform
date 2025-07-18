"""
Script de migration pour ajouter le champ user_id aux anciennes données de santé (collection donnees).
- À utiliser une seule fois après ajout du champ user_id dans le modèle Donnee.
- Remplit user_id manquant avec un ID choisi (exemple : lier à un patient de test, ou à l'admin pour archivage).
- À adapter selon la stratégie RGPD choisie.
"""

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "sante_db")
COLLECTION = "donnees"

# À adapter : ID du patient à utiliser pour les anciennes données
USER_ID_DEFAUT = "ID_DU_PATIENT_DE_TEST"  # Remplacer par un vrai ObjectId patient

async def migrer():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION]

    # Cherche toutes les données sans user_id
    cursor = collection.find({"user_id": {"$exists": False}})
    n = 0
    async for doc in cursor:
        # Ajoute le champ user_id par défaut
        await collection.update_one({"_id": doc["_id"]}, {"$set": {"user_id": USER_ID_DEFAUT}})
        n += 1
    print(f"Migration terminée : {n} documents mis à jour.")

if __name__ == "__main__":
    asyncio.run(migrer())
