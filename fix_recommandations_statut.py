#!/usr/bin/env python3
"""
Script pour corriger les statuts manquants des recommandations
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def fix_statuts():
    # Connexion MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== CORRECTION STATUTS RECOMMANDATIONS ===")
    
    # 1. Vérifier l'état actuel
    total_recos = await db.recommandations.count_documents({})
    recos_sans_statut = await db.recommandations.count_documents({"statut": {"$exists": False}})
    recos_statut_vide = await db.recommandations.count_documents({"statut": None})
    
    print(f"Total recommandations: {total_recos}")
    print(f"Sans champ statut: {recos_sans_statut}")
    print(f"Statut null/vide: {recos_statut_vide}")
    
    # 2. Corriger toutes les recommandations sans statut ou avec statut vide
    query_to_fix = {
        "$or": [
            {"statut": {"$exists": False}},
            {"statut": None},
            {"statut": ""}
        ]
    }
    
    update_result = await db.recommandations.update_many(
        query_to_fix,
        {"$set": {"statut": "nouvelle"}}
    )
    
    print(f"Recommandations corrigées: {update_result.modified_count}")
    
    # 3. Vérifier le résultat
    recos_nouvelles = await db.recommandations.count_documents({"statut": "nouvelle"})
    print(f"Recommandations avec statut 'nouvelle': {recos_nouvelles}")
    
    # 4. Afficher quelques exemples
    print("\n=== EXEMPLES APRÈS CORRECTION ===")
    recos_cursor = db.recommandations.find({}).limit(3)
    recos = await recos_cursor.to_list(None)
    
    for reco in recos:
        print(f"ID: {reco['_id']}")
        print(f"  User ID: {reco.get('user_id')}")
        print(f"  Statut: {reco.get('statut')}")
        print(f"  Date: {reco.get('date')}")
        print()
    
    client.close()
    print("✅ Correction terminée !")

if __name__ == "__main__":
    asyncio.run(fix_statuts())
