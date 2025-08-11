#!/usr/bin/env python3
"""
Script pour assigner des patients à des médecins et tester les nouvelles fonctionnalités.
"""

import asyncio
import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Configuration MongoDB
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "sante_db"

async def main():
    """Assigner des patients aux médecins et mettre à jour les statuts."""
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("=== Assignation Medecin-Patient ===")
        
        # 1. Récupérer les utilisateurs existants
        patients = await db.utilisateurs.find({"role": "patient"}).to_list(None)
        medecins = await db.utilisateurs.find({"role": "medecin"}).to_list(None)
        
        print(f"📋 Patients trouvés: {len(patients)}")
        print(f"👨‍⚕️ Médecins trouvés: {len(medecins)}")
        
        if not patients or not medecins:
            print("❌ Aucun patient ou médecin trouvé. Veuillez d'abord créer des utilisateurs.")
            return
        
        # 2. Assigner chaque patient au premier médecin disponible
        medecin = medecins[0]  # Prendre le premier médecin
        medecin_id = str(medecin["_id"])
        
        print(f"\n👨‍⚕️ Assignation au médecin: {medecin['username']} ({medecin['email']})")
        
        for patient in patients:
            patient_id = str(patient["_id"])
            
            # Mettre à jour le patient (ajouter le médecin)
            await db.utilisateurs.update_one(
                {"_id": patient["_id"]},
                {
                    "$addToSet": {"medecin_ids": medecin_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Mettre à jour le médecin (ajouter le patient)
            await db.utilisateurs.update_one(
                {"_id": medecin["_id"]},
                {
                    "$addToSet": {"patient_ids": patient_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            print(f"✅ Patient {patient['username']} assigné au médecin {medecin['username']}")
        
        # 3. Mettre à jour les alertes et recommandations existantes avec les nouveaux champs
        print("\n🔄 Mise à jour des alertes et recommandations...")
        
        # Mettre à jour les alertes
        alertes_result = await db.alertes.update_many(
            {"statut": {"$exists": False}},
            {
                "$set": {
                    "statut": "nouvelle",
                    "vue_par": "",
                    "date_vue": None,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        print(f"✅ {alertes_result.modified_count} alertes mises à jour")
        
        # Mettre à jour les recommandations
        recos_result = await db.recommandations.update_many(
            {"statut": {"$exists": False}},
            {
                "$set": {
                    "statut": "nouvelle",
                    "vue_par": "",
                    "date_vue": None,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        print(f"✅ {recos_result.modified_count} recommandations mises à jour")
        
        # 4. Afficher un résumé des assignations
        print(f"\n📊 === Résumé des Assignations ===")
        
        medecin_updated = await db.utilisateurs.find_one({"_id": medecin["_id"]})
        print(f"👨‍⚕️ Médecin: {medecin_updated['username']}")
        print(f"   📋 Patients assignés: {len(medecin_updated.get('patient_ids', []))}")
        
        for patient in patients:
            patient_updated = await db.utilisateurs.find_one({"_id": patient["_id"]})
            print(f"👤 Patient: {patient_updated['username']}")
            print(f"   👨‍⚕️ Médecins assignés: {len(patient_updated.get('medecin_ids', []))}")
        
        # 5. Statistiques des alertes/recommandations
        total_alertes = await db.alertes.count_documents({})
        nouvelles_alertes = await db.alertes.count_documents({"statut": "nouvelle"})
        
        total_recos = await db.recommandations.count_documents({})
        nouvelles_recos = await db.recommandations.count_documents({"statut": "nouvelle"})
        
        print(f"\n📈 === Statistiques ===")
        print(f"🚨 Alertes: {nouvelles_alertes}/{total_alertes} nouvelles")
        print(f"💡 Recommandations: {nouvelles_recos}/{total_recos} nouvelles")
        
        print(f"\n✅ Assignation terminée avec succès!")
        print(f"🔗 Les médecins peuvent maintenant accéder à /medecin pour voir leurs patients")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'assignation: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
