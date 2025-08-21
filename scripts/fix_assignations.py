#!/usr/bin/env python3
"""Script pour corriger les assignations médecin-patient dans MongoDB.
Assigne TestP1 aux médecins Doc1, Doc2, Doc3 pour qu'ils puissent voir les alertes.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Configuration MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sante_db")

async def fix_assignations():
    """Corrige les assignations médecin-patient."""
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    
    print("Verification des utilisateurs...")
    
    # Trouver TestP1 (patient)
    patient = await db.utilisateurs.find_one({"username": "testP1", "role": "patient"})
    if not patient:
        print("Patient TestP1 introuvable")
        return
    
    patient_id = str(patient["_id"])
    print(f"Patient TestP1 trouve: {patient_id}")
    
    # Trouver les médecins Doc1, Doc2, Doc3
    medecins = []
    for doc_name in ["Doc1", "Doc2", "Doc3"]:
        medecin = await db.utilisateurs.find_one({"username": doc_name, "role": "medecin"})
        if medecin:
            medecins.append({"username": doc_name, "id": str(medecin["_id"])})
            print(f"Medecin {doc_name} trouve: {medecin['_id']}")
        else:
            print(f"Medecin {doc_name} introuvable")
    
    if not medecins:
        print("Aucun medecin trouve")
        return
    
    print(f"\nAssignation de TestP1 aux {len(medecins)} medecins...")
    
    # SEGREGATION RBAC: Assigner TestP1 UNIQUEMENT à Doc1 (relation 1:1)
    doc1_id = None
    for m in medecins:
        if m["username"] == "Doc1":
            doc1_id = m["id"]
            break
    
    if not doc1_id:
        print("Doc1 introuvable pour assignation unique")
        return
    
    # Mettre à jour le patient avec UN SEUL médecin référent
    await db.utilisateurs.update_one(
        {"_id": ObjectId(patient_id)},
        {"$set": {"medecin_ids": [doc1_id]}}
    )
    print(f"Patient TestP1 assigne UNIQUEMENT a Doc1: {doc1_id}")
    
    # Mettre à jour Doc1 avec ce patient
    await db.utilisateurs.update_one(
        {"_id": ObjectId(doc1_id)},
        {"$addToSet": {"patient_ids": patient_id}}
    )
    print(f"Doc1 mis a jour avec patient TestP1")
    
    # Nettoyer les autres médecins (retirer TestP1 de leurs listes)
    for medecin in medecins:
        if medecin["id"] != doc1_id:
            await db.utilisateurs.update_one(
                {"_id": ObjectId(medecin["id"])},
                {"$pull": {"patient_ids": patient_id}}
            )
            print(f"Patient retire de {medecin['username']}")
    
    # Vérifier les alertes de TestP1
    alertes_count = await db.alertes.count_documents({"user_id": patient_id})
    print(f"\nAlertes trouvees pour TestP1: {alertes_count}")
    
    if alertes_count > 0:
        # Afficher quelques alertes
        async for alerte in db.alertes.find({"user_id": patient_id}).limit(3):
            print(f"   - {alerte.get('message', 'Sans message')} (niveau: {alerte.get('niveau', 'N/A')})")
    
    # Fermer la connexion
    client.close()
    print("\nAssignations corrigees avec succes !")
    print("Les medecins Doc1, Doc2, Doc3 peuvent maintenant voir les alertes de TestP1")

if __name__ == "__main__":
    asyncio.run(fix_assignations())
