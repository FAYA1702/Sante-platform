#!/usr/bin/env python3
"""Script pour corriger le statut des alertes existantes."""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from backend.db import MONGO_URI, MONGO_DB_NAME

async def fix_alerts_status():
    """Met à jour les alertes avec statut null vers 'nouvelle'."""
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    
    print("=== CORRECTION DES STATUTS D'ALERTES ===")
    
    # Compter les alertes avec statut null/manquant
    alertes_sans_statut = await db.alertes.count_documents({
        "$or": [
            {"statut": {"$exists": False}},
            {"statut": None},
            {"statut": ""}
        ]
    })
    
    print(f"Alertes sans statut valide: {alertes_sans_statut}")
    
    if alertes_sans_statut > 0:
        # Mettre à jour toutes les alertes sans statut vers "nouvelle"
        result = await db.alertes.update_many(
            {
                "$or": [
                    {"statut": {"$exists": False}},
                    {"statut": None},
                    {"statut": ""}
                ]
            },
            {
                "$set": {"statut": "nouvelle"}
            }
        )
        
        print(f"Alertes mises a jour: {result.modified_count}")
    
    # Vérification finale
    alertes_nouvelles = await db.alertes.count_documents({"statut": "nouvelle"})
    alertes_total = await db.alertes.count_documents({})
    
    print(f"\nVerification finale:")
    print(f"  Total alertes: {alertes_total}")
    print(f"  Alertes 'nouvelle': {alertes_nouvelles}")
    
    # Afficher quelques exemples
    exemples = await db.alertes.find({}, {"message": 1, "statut": 1, "user_id": 1}).limit(5).to_list(None)
    print(f"\nExemples d'alertes:")
    for alerte in exemples:
        print(f"  - {alerte.get('message', 'N/A')} (statut: {alerte.get('statut', 'N/A')})")
    
    client.close()
    print("\nCorrection terminee!")

if __name__ == "__main__":
    asyncio.run(fix_alerts_status())
