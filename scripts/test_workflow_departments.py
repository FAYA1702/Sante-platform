#!/usr/bin/env python3
"""Script de test complet du workflow départements médicaux.
Teste : Injection donnée → Alerte IA → Orientation → Assignation
Tous les commentaires sont rédigés en français.
"""

import asyncio
import os
import redis.asyncio as redis
import json
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

# Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sante_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

async def test_complete_workflow():
    """Test complet du workflow départements médicaux."""
    
    print("=== TEST WORKFLOW COMPLET DEPARTEMENTS MEDICAUX ===")
    
    # Connexions
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client[MONGO_DB_NAME]
    redis_client = redis.from_url(REDIS_URL)
    
    try:
        # Étape 1: Trouver un patient existant
        print("\n1. Recherche d'un patient...")
        patient = await db.utilisateurs.find_one({"role": "patient"})
        if not patient:
            print("ERREUR: Aucun patient trouve")
            return
        print(f"Patient trouve: {patient['username']} (ID: {patient['_id']})")
        
        # Étape 2: Injecter une donnée de santé avec tachycardie
        print("\n2. Injection d'une donnee de sante (tachycardie)...")
        donnee_sante = {
            "user_id": str(patient["_id"]),
            "frequence_cardiaque": 125,  # Tachycardie (> 100)
            "taux_oxygene": 95,
            "pression_arterielle": "140/90",
            "date": datetime.utcnow(),
            "device_id": "test_device_001",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = await db.donnees.insert_one(donnee_sante)
        donnee_id = str(result.inserted_id)
        print(f"Donnee inseree: ID {donnee_id}, FC: {donnee_sante['frequence_cardiaque']} bpm")
        
        # Étape 3: Publier l'événement Redis pour déclencher l'IA
        print("\n3. Publication evenement Redis pour declencher l'IA...")
        event_data = {
            "donnee_id": donnee_id,
            "user_id": str(patient["_id"]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await redis_client.publish("nouvelle_donnee", json.dumps(event_data))
        print("Evenement publie sur canal 'nouvelle_donnee'")
        
        # Étape 4: Attendre et vérifier la génération d'alerte
        print("\n4. Attente de la generation d'alerte par l'IA (3 secondes)...")
        await asyncio.sleep(3)
        
        # Vérifier les alertes générées
        alertes = await db.alertes.find({"user_id": str(patient["_id"])}).sort("date", -1).limit(1).to_list(length=1)
        if alertes:
            alerte = alertes[0]
            print(f"Alerte generee: {alerte['message']}")
            print(f"Niveau: {alerte['niveau']}")
            if 'suggested_department_code' in alerte:
                print(f"Departement suggere: {alerte['suggested_department_code']}")
        else:
            print("ATTENTION: Aucune alerte generee")
        
        # Étape 5: Vérifier la création d'orientation (referral)
        print("\n5. Verification des orientations creees...")
        referrals = await db.referrals.find({"patient_id": str(patient["_id"])}).sort("created_at", -1).limit(1).to_list(length=1)
        if referrals:
            referral = referrals[0]
            print(f"Orientation creee: ID {referral['_id']}")
            print(f"Statut: {referral['status']}")
            print(f"Source: {referral['source']}")
            print(f"Notes: {referral.get('notes', 'N/A')}")
            
            # Récupérer le nom du département
            dept = await db.departments.find_one({"_id": ObjectId(referral["proposed_department_id"])})
            if dept:
                print(f"Departement propose: {dept['name']} ({dept['code']})")
        else:
            print("ATTENTION: Aucune orientation creee")
        
        # Étape 6: Vérifier les recommandations générées
        print("\n6. Verification des recommandations generees...")
        recommendations = await db.recommandations.find({"user_id": str(patient["_id"])}).sort("created_at", -1).limit(1).to_list(length=1)
        if recommendations:
            rec = recommendations[0]
            print(f"Recommandation generee: {rec.get('titre', 'N/A')}")
            print(f"Description: {rec.get('description', rec.get('contenu', 'N/A'))[:100]}...")
        else:
            print("ATTENTION: Aucune recommandation generee")
        
        print("\n=== RESUME DU TEST ===")
        print(f"Patient: {patient['username']}")
        print(f"Donnee FC: {donnee_sante['frequence_cardiaque']} bpm (tachycardie)")
        print(f"Alertes: {len(alertes)} generee(s)")
        print(f"Orientations: {len(referrals)} creee(s)")
        print(f"Recommandations: {len(recommendations)} generee(s)")
        
        if alertes and referrals:
            print("\nSUCCES: Workflow complet fonctionne !")
        else:
            print("\nATTENTION: Workflow incomplet, verifier les logs du microservice IA")
            
    except Exception as e:
        print(f"ERREUR: {e}")
    finally:
        # Fermer les connexions
        await redis_client.close()
        mongo_client.close()

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
