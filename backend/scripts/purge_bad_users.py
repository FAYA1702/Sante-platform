"""
Script de nettoyage MongoDB : supprime tous les utilisateurs dont le username n'est pas lisible (ObjectId, trop court, ou vide).
À lancer manuellement pour repartir sur une base propre avant la démo.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import re

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "sante_db"
COLLECTION = "utilisateurs"

# Username valide : au moins 3 caractères, lettres/chiffres/._-
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_.-]{3,}$")

async def purge_bad_users():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    users = db[COLLECTION]
    # Sélectionne les utilisateurs à supprimer (username absent, trop court, ou non conforme)
    query = {
        "$or": [
            {"username": {"$exists": False}},
            {"username": {"$type": "objectId"}},
            {"username": {"$type": "null"}},
            {"username": {"$not": {"$regex": r"^[a-zA-Z0-9_.-]{3,}$"}}}
        ]
    }
    to_delete = await users.count_documents(query)
    if to_delete == 0:
        print("Aucun utilisateur à supprimer.")
        return
    result = await users.delete_many(query)
    print(f"Utilisateurs supprimés : {result.deleted_count}")

if __name__ == "__main__":
    asyncio.run(purge_bad_users())
