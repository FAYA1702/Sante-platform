#!/usr/bin/env python3
"""
Générer des données de test pour chaque patient pour valider la ségrégation
"""
import asyncio
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis

async def generate_test_data():
    # Connexions
    mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
    redis_client = await redis.from_url("redis://localhost:6379", decode_responses=True)
    db = mongo_client["sante_db"]
    
    print("=== GENERATION DONNEES TEST ===")
    
    # Récupérer les patients
    patients_cursor = db.utilisateurs.find({"role": "patient"})
    patients = await patients_cursor.to_list(None)
    
    print(f"Patients trouvés: {len(patients)}")
    
    for i, patient in enumerate(patients):
        patient_id = str(patient["_id"])
        username = patient["username"]
        
        print(f"\n--- Patient {username} ({patient_id}) ---")
        
        # Générer 2 données de santé différentes pour chaque patient
        donnees = []
        
        if username == "patient":
            # Patient 1: Tachycardie (FC > 100)
            donnees = [
                {
                    "user_id": patient_id,
                    "frequence_cardiaque": 110,  # Tachycardie
                    "taux_oxygene": 95,
                    "tension_arterielle": "130/80",
                    "date": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "is_active": True
                },
                {
                    "user_id": patient_id,
                    "frequence_cardiaque": 105,  # Tachycardie
                    "taux_oxygene": 94,
                    "tension_arterielle": "125/75",
                    "date": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "is_active": True
                }
            ]
        elif username == "mor":
            # Patient 2: Hypoxie (SpO2 < 92)
            donnees = [
                {
                    "user_id": patient_id,
                    "frequence_cardiaque": 85,
                    "taux_oxygene": 90,  # Hypoxie
                    "tension_arterielle": "120/70",
                    "date": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "is_active": True
                },
                {
                    "user_id": patient_id,
                    "frequence_cardiaque": 88,
                    "taux_oxygene": 89,  # Hypoxie
                    "tension_arterielle": "118/68",
                    "date": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "is_active": True
                }
            ]
        
        # Insérer les données et publier sur Redis
        for j, donnee in enumerate(donnees):
            # Insérer en base
            result = await db.donnees.insert_one(donnee)
            donnee_id = str(result.inserted_id)
            
            print(f"  Donnée {j+1} insérée: {donnee_id}")
            print(f"    FC: {donnee['frequence_cardiaque']}, SpO2: {donnee['taux_oxygene']}")
            
            # Publier sur Redis pour déclencher l'IA
            payload = {"donnee_id": donnee_id}
            await redis_client.publish("nouvelle_donnee", json.dumps(payload))
            print(f"    Publié sur Redis: {payload}")
            
            # Attendre un peu pour que l'IA traite
            await asyncio.sleep(2)
    
    # Attendre que l'IA termine le traitement
    print("\nAttente traitement IA...")
    await asyncio.sleep(5)
    
    # Vérifier les résultats
    print("\n=== VERIFICATION RESULTATS ===")
    
    for patient in patients:
        patient_id = str(patient["_id"])
        username = patient["username"]
        
        # Compter les données
        donnees_count = await db.donnees.count_documents({"user_id": patient_id})
        
        # Compter les alertes
        alertes_count = await db.alertes.count_documents({"user_id": patient_id})
        
        # Compter les recommandations
        recos_count = await db.recommandations.count_documents({"user_id": patient_id})
        recos_nouvelles = await db.recommandations.count_documents({"user_id": patient_id, "statut": "nouvelle"})
        
        print(f"\nPatient {username} ({patient_id}):")
        print(f"  Données: {donnees_count}")
        print(f"  Alertes: {alertes_count}")
        print(f"  Recommandations: {recos_count} (nouvelles: {recos_nouvelles})")
    
    await mongo_client.close()
    await redis_client.close()
    print("\nGeneration terminee!")

if __name__ == "__main__":
    asyncio.run(generate_test_data())
