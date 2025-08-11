#!/usr/bin/env python3
"""
Script de diagnostic complet pour le problème des recommandations médecin
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

async def debug_medecin():
    try:
        # Connexion MongoDB
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['sante_db']
        
        print("=== DIAGNOSTIC MÉDECIN ===")
        
        # 1. Vérifier les collections existantes
        collections = await db.list_collection_names()
        print(f"Collections: {collections}")
        
        # 2. Vérifier les utilisateurs
        users = await db.utilisateurs.find({}, {"username": 1, "role": 1, "medecin_ids": 1, "patient_ids": 1}).to_list(None)
        print(f"\nUtilisateurs ({len(users)}):")
        for user in users:
            print(f"  - {user.get('username', 'N/A')} ({user.get('role', 'N/A')}) - ID: {user['_id']}")
            if user.get('role') == 'patient' and 'medecin_ids' in user:
                print(f"    Médecins assignés: {user.get('medecin_ids', [])}")
            if user.get('role') == 'medecin' and 'patient_ids' in user:
                print(f"    Patients assignés: {user.get('patient_ids', [])}")
        
        # 3. Vérifier les recommandations
        recos_count = await db.recommandations.count_documents({})
        print(f"\nRecommandations totales: {recos_count}")
        
        if recos_count > 0:
            recos = await db.recommandations.find({}, {"user_id": 1, "titre": 1, "statut": 1}).to_list(5)
            print("Premières recommandations:")
            for reco in recos:
                print(f"  - {reco.get('titre', 'N/A')} (user_id: {reco.get('user_id')}, statut: {reco.get('statut')})")
        
        # 4. Vérifier les alertes
        alertes_count = await db.alertes.count_documents({})
        print(f"\nAlertes totales: {alertes_count}")
        
        if alertes_count > 0:
            alertes = await db.alertes.find({}, {"user_id": 1, "message": 1, "statut": 1}).to_list(5)
            print("Premières alertes:")
            for alerte in alertes:
                print(f"  - {alerte.get('message', 'N/A')} (user_id: {alerte.get('user_id')}, statut: {alerte.get('statut')})")
        
        # 5. Si pas de données, les créer
        if recos_count == 0:
            print("\n=== CRÉATION DE DONNÉES DE TEST ===")
            
            # Trouver un médecin et des patients
            medecin = await db.utilisateurs.find_one({"role": "medecin"})
            patients = await db.utilisateurs.find({"role": "patient"}).to_list(2)
            
            if not medecin:
                print("❌ Aucun médecin trouvé")
                return
            
            if len(patients) == 0:
                print("❌ Aucun patient trouvé")
                return
            
            medecin_id = str(medecin['_id'])
            print(f"Médecin: {medecin.get('username')} (ID: {medecin_id})")
            
            # Assigner les patients au médecin
            patient_ids = []
            for patient in patients:
                patient_id = str(patient['_id'])
                patient_ids.append(patient_id)
                
                # Mettre à jour l'association médecin-patient
                await db.utilisateurs.update_one(
                    {"_id": patient['_id']},
                    {"$addToSet": {"medecin_ids": medecin_id}}
                )
                await db.utilisateurs.update_one(
                    {"_id": medecin['_id']},
                    {"$addToSet": {"patient_ids": patient_id}}
                )
                print(f"Patient assigné: {patient.get('username')} (ID: {patient_id})")
            
            # Créer des recommandations de test
            recommandations_test = []
            for i, patient in enumerate(patients):
                patient_id = str(patient['_id'])
                username = patient.get('username', f'Patient{i+1}')
                
                recommandations_test.extend([
                    {
                        'user_id': patient_id,
                        'titre': f'Surveillance cardiaque - {username}',
                        'description': f'Recommandation de surveillance continue pour {username}',
                        'contenu': 'Surveillance cardiaque recommandée suite à anomalie détectée',
                        'date': datetime.now(),
                        'statut': 'nouvelle',
                        'priorite_medicale': 'elevee',
                        'visible_patient': True,
                        'validation_medicale': False
                    },
                    {
                        'user_id': patient_id,
                        'titre': f'Consultation urgente - {username}',
                        'description': f'Consultation médicale urgente pour {username}',
                        'contenu': 'Consultation urgente nécessaire suite à valeurs critiques',
                        'date': datetime.now(),
                        'statut': 'nouvelle',
                        'priorite_medicale': 'critique',
                        'visible_patient': False,
                        'validation_medicale': False
                    }
                ])
            
            # Insérer les recommandations
            if recommandations_test:
                result = await db.recommandations.insert_many(recommandations_test)
                print(f"✅ {len(result.inserted_ids)} recommandations créées")
            
            # Créer des alertes de test aussi
            alertes_test = []
            for i, patient in enumerate(patients):
                patient_id = str(patient['_id'])
                username = patient.get('username', f'Patient{i+1}')
                
                alertes_test.extend([
                    {
                        'user_id': patient_id,
                        'message': f'Tachycardie détectée chez {username}',
                        'niveau': 'warning',
                        'date': datetime.now(),
                        'statut': 'nouvelle',
                        'priorite_medicale': 'elevee',
                        'visible_patient': True
                    },
                    {
                        'user_id': patient_id,
                        'message': f'Hypoxie critique chez {username}',
                        'niveau': 'critical',
                        'date': datetime.now(),
                        'statut': 'nouvelle',
                        'priorite_medicale': 'critique',
                        'visible_patient': False
                    }
                ])
            
            if alertes_test:
                result = await db.alertes.insert_many(alertes_test)
                print(f"✅ {len(result.inserted_ids)} alertes créées")
        
        print("\n=== DIAGNOSTIC TERMINÉ ===")
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    asyncio.run(debug_medecin())
