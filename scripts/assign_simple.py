#!/usr/bin/env python3
"""
Script simple pour assigner des patients à des médecins.
"""

import asyncio
import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient

# Configuration MongoDB
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "sante_db"

async def main():
    """Assigner des patients aux médecins."""
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("=== Assignation Medecin-Patient ===")
        
        # 1. Récupérer les utilisateurs existants
        patients = await db.utilisateurs.find({"role": "patient"}).to_list(None)
        medecins = await db.utilisateurs.find({"role": "medecin"}).to_list(None)
        
        print(f"Patients trouvés: {len(patients)}")
        print(f"Médecins trouvés: {len(medecins)}")
        
        if not patients or not medecins:
            print("ERREUR: Aucun patient ou médecin trouvé.")
            return
        
        # 2. Assigner chaque patient au premier médecin disponible
        medecin = medecins[0]
        medecin_id = str(medecin["_id"])
        
        print(f"Assignation au médecin: {medecin['username']}")
        
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
            
            print(f"OK: Patient {patient['username']} assigné")
        
        # 3. Mettre à jour les alertes et recommandations
        print("Mise à jour des alertes et recommandations...")
        
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
        print(f"Alertes mises à jour: {alertes_result.modified_count}")
        
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
        print(f"Recommandations mises à jour: {recos_result.modified_count}")
        
        # 4. Statistiques
        total_alertes = await db.alertes.count_documents({})
        nouvelles_alertes = await db.alertes.count_documents({"statut": "nouvelle"})
        
        total_recos = await db.recommandations.count_documents({})
        nouvelles_recos = await db.recommandations.count_documents({"statut": "nouvelle"})
        
        print(f"Alertes: {nouvelles_alertes}/{total_alertes} nouvelles")
        print(f"Recommandations: {nouvelles_recos}/{total_recos} nouvelles")
        
        print("Assignation terminée avec succès!")
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
