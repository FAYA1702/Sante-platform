#!/usr/bin/env python3
"""
Vérifier les utilisateurs en base
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_users():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== VERIFICATION UTILISATEURS ===")
    
    # Tous les utilisateurs
    users_cursor = db.utilisateurs.find({})
    users = await users_cursor.to_list(None)
    
    print(f"Total utilisateurs: {len(users)}")
    
    for user in users:
        print(f"\nUsername: {user['username']}")
        print(f"Email: {user.get('email', 'N/A')}")
        print(f"Role: {user['role']}")
        print(f"ID: {user['_id']}")
        if user['role'] == 'medecin':
            print(f"Patients: {user.get('patient_ids', [])}")
        elif user['role'] == 'patient':
            print(f"Medecins: {user.get('medecin_ids', [])}")
    
    # Vérifier les recommandations par user_id
    print(f"\n=== RECOMMANDATIONS PAR PATIENT ===")
    for user in users:
        if user['role'] == 'patient':
            user_id_str = str(user['_id'])
            recos_count = await db.recommandations.count_documents({"user_id": user_id_str})
            recos_statut = await db.recommandations.count_documents({"user_id": user_id_str, "statut": "nouvelle"})
            print(f"Patient {user['username']} ({user_id_str}):")
            print(f"  Total recommandations: {recos_count}")
            print(f"  Statut 'nouvelle': {recos_statut}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_users())
