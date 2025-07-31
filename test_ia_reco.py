import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from bson import ObjectId

# CONFIGURATION
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB_NAME", "sante_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
USER_ID = "test_user_ia"

async def main():
    # Connexion MongoDB
    mongo = AsyncIOMotorClient(MONGO_URI)
    db = mongo[MONGO_DB]

    # Création d'une donnée anormale (tachycardie)
    donnee = {
        "utilisateur_id": USER_ID,
        "frequence_cardiaque": 130,  # supérieur à FC_MAX
        "taux_oxygene": 98,
        "date": datetime.utcnow().isoformat(),
    }
    result = await db["donnees"].insert_one(donnee)
    donnee_id = str(result.inserted_id)
    print(f"Donnée insérée avec _id={donnee_id}")

    # Publication sur Redis
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    payload = {"donnee_id": donnee_id}
    import json
    await redis_client.publish("nouvelle_donnee", json.dumps(payload))
    print("Événement publié sur Redis")

    # Attendre que l'IA traite
    await asyncio.sleep(5)

    # Vérifier la recommandation
    reco = await db["recommandations"].find_one({"user_id": USER_ID})
    if reco:
        print("\033[92mRecommandation générée :\033[0m", reco)
    else:
        print("\033[91mAucune recommandation générée.\033[0m")

    # Nettoyage (optionnel)
    await db["donnees"].delete_one({"_id": ObjectId(donnee_id)})
    await db["recommandations"].delete_many({"user_id": USER_ID})
    mongo.close()
    await redis_client.close()

if __name__ == "__main__":
    asyncio.run(main())
