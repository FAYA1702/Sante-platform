#!/usr/bin/env python3
"""
Diagnostic complet de toutes les alertes dans la base de données
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def debug_all_alerts():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== DIAGNOSTIC COMPLET ALERTES ===")
    
    # 1. Lister tous les utilisateurs
    print("1. UTILISATEURS:")
    utilisateurs = await db.utilisateurs.find({}).to_list(None)
    user_map = {}
    for user in utilisateurs:
        user_id = str(user["_id"])
        user_map[user_id] = user
        print(f"   {user['username']} ({user['role']}) - ID: {user_id}")
    
    print(f"\nTotal utilisateurs: {len(utilisateurs)}")
    
    # 2. Lister toutes les alertes
    print("\n2. TOUTES LES ALERTES:")
    alertes = await db.alertes.find({}).to_list(None)
    print(f"Total alertes: {len(alertes)}")
    
    for i, alerte in enumerate(alertes, 1):
        user_id = alerte.get('user_id', 'N/A')
        user_info = user_map.get(user_id, {'username': 'INCONNU', 'role': 'N/A'})
        
        print(f"\n   Alerte {i}:")
        print(f"     ID: {alerte.get('_id', 'N/A')}")
        print(f"     Message: {alerte.get('message', 'N/A')}")
        print(f"     Niveau: {alerte.get('niveau', 'N/A')}")
        print(f"     User ID: {user_id}")
        print(f"     Patient: {user_info['username']} ({user_info['role']})")
        print(f"     Date: {alerte.get('timestamp', 'N/A')}")
        print(f"     Statut: {alerte.get('statut', 'N/A')}")
    
    # 3. Vérifier spécifiquement le patient "fall"
    print("\n3. PATIENT 'fall' SPÉCIFIQUE:")
    patient_fall = await db.utilisateurs.find_one({"username": "fall", "role": "patient"})
    
    if patient_fall:
        fall_id = str(patient_fall["_id"])
        print(f"Patient fall ID: {fall_id}")
        
        # Alertes du patient fall
        alertes_fall = await db.alertes.find({"user_id": fall_id}).to_list(None)
        print(f"Alertes pour patient fall: {len(alertes_fall)}")
        
        for alerte in alertes_fall:
            print(f"   - {alerte.get('message', 'N/A')} ({alerte.get('niveau', 'N/A')})")
        
        # Données du patient fall
        donnees_fall = await db.donnees.find({"user_id": fall_id}).to_list(None)
        print(f"Données pour patient fall: {len(donnees_fall)}")
    
    # 4. Vérifier les autres patients avec des alertes
    print("\n4. AUTRES PATIENTS AVEC ALERTES:")
    for user_id, count in [(a.get('user_id'), 1) for a in alertes]:
        if user_id and user_id in user_map:
            user_info = user_map[user_id]
            if user_info['username'] != 'fall':
                alertes_user = await db.alertes.count_documents({"user_id": user_id})
                if alertes_user > 0:
                    print(f"   {user_info['username']} ({user_info['role']}): {alertes_user} alertes")
    
    client.close()
    print("\nDiagnostic terminé!")

if __name__ == "__main__":
    asyncio.run(debug_all_alerts())
