"""
Script de migration pour mettre à jour les documents Recommandation existants.
Ajoute les champs titre et description manquants avec des valeurs par défaut.
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateMany
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de la connexion MongoDB
MONGO_URI = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB", "sante_db")

async def migrate_recommandations():
    """Migre les documents Recommandation existants."""
    print("Début de la migration des recommandations...")
    
    # Se connecter à MongoDB
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db["recommandations"]
    
    try:
        # Compter les documents à mettre à jour
        count = await collection.count_documents({
            "$or": [
                {"titre": {"$exists": False}},
                {"description": {"$exists": False}}
            ]
        })
        
        if count == 0:
            print("Aucune recommandation à mettre à jour.")
            return
            
        print(f"Mise à jour de {count} recommandations...")
        
        # Mettre à jour les documents
        result = await collection.update_many(
            {
                "$or": [
                    {"titre": {"$exists": False}},
                    {"description": {"$exists": False}}
                ]
            },
            [
                {
                    "$set": {
                        "titre": {
                            "$cond": [
                                {"$ifNull": ["$titre", False]},
                                "$titre",
                                {
                                    "$cond": [
                                        {"$ifNull": ["$contenu", False]},
                                        {"$substrCP": ["$contenu", 0, 50]},
                                        "Recommandation de santé"
                                    ]
                                }
                            ]
                        },
                        "description": {
                            "$cond": [
                                {"$ifNull": ["$description", False]},
                                "$description",
                                {"$ifNull": ["$contenu", "Aucune description disponible"]}
                            ]
                        },
                        "updated_at": datetime.utcnow()
                    }
                }
            ]
        )
        
        print(f"Migration terminée. {result.modified_count} documents mis à jour.")
        
    except Exception as e:
        print(f"Erreur lors de la migration: {e}")
    finally:
        # Fermer la connexion
        client.close()

if __name__ == "__main__":
    asyncio.run(migrate_recommandations())
