#!/usr/bin/env python3
"""
Script de création directe d'alertes et recommandations de test
pour valider le filtrage par patient côté médecin
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

async def create_test_data():
    try:
        # Connexion MongoDB
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['sante_db']
        
        # Récupérer tous les patients
        patients_cursor = db.utilisateurs.find({'role': 'patient'})
        patients = await patients_cursor.to_list(None)
        
        if len(patients) < 2:
            print('Pas assez de patients trouvés')
            return
        
        print(f'Patients trouvés: {len(patients)}')
        
        # Créer des alertes de test pour chaque patient
        alertes_test = []
        recommandations_test = []
        
        for i, patient in enumerate(patients[:2]):  # Limiter à 2 patients
            patient_id = str(patient['_id'])
            username = patient.get('username', 'Patient inconnu')
            
            print(f'Création de données pour: {username} (ID: {patient_id})')
            
            # Alertes pour ce patient
            alertes_test.extend([
                {
                    '_id': ObjectId(),
                    'user_id': patient_id,
                    'message': f'Tachycardie détectée chez {username}',
                    'niveau': 'warning',
                    'date': datetime.now(),
                    'statut': 'nouvelle',
                    'priorite_medicale': 'elevee',
                    'visible_patient': True
                },
                {
                    '_id': ObjectId(),
                    'user_id': patient_id,
                    'message': f'Hypoxie critique détectée chez {username}',
                    'niveau': 'critical',
                    'date': datetime.now(),
                    'statut': 'nouvelle',
                    'priorite_medicale': 'critique',
                    'visible_patient': False  # Masquée au patient
                }
            ])
            
            # Recommandations pour ce patient
            recommandations_test.extend([
                {
                    '_id': ObjectId(),
                    'user_id': patient_id,
                    'titre': f'Surveillance cardiaque pour {username}',
                    'description': 'Recommandation de surveillance continue de la fréquence cardiaque',
                    'contenu': 'Surveillance cardiaque recommandée suite à tachycardie détectée',
                    'date': datetime.now(),
                    'statut': 'nouvelle',
                    'priorite_medicale': 'elevee',
                    'visible_patient': True,
                    'validation_medicale': False
                },
                {
                    '_id': ObjectId(),
                    'user_id': patient_id,
                    'titre': f'Consultation urgente pour {username}',
                    'description': 'Consultation médicale urgente recommandée',
                    'contenu': 'Consultation urgente nécessaire suite à hypoxie critique',
                    'date': datetime.now(),
                    'statut': 'nouvelle',
                    'priorite_medicale': 'critique',
                    'visible_patient': False,  # Masquée au patient
                    'validation_medicale': False
                }
            ])
        
        # Insérer les alertes
        if alertes_test:
            result_alertes = await db.alertes.insert_many(alertes_test)
            print(f'Alertes créées: {len(result_alertes.inserted_ids)}')
        
        # Insérer les recommandations
        if recommandations_test:
            result_recos = await db.recommandations.insert_many(recommandations_test)
            print(f'Recommandations créées: {len(result_recos.inserted_ids)}')
        
        client.close()
        print('Création de données de test terminée avec succès!')
        
        # Afficher un résumé
        print('\n=== RÉSUMÉ ===')
        for patient in patients[:2]:
            patient_id = str(patient['_id'])
            username = patient.get('username', 'Patient inconnu')
            print(f'Patient: {username} (ID: {patient_id})')
            print(f'  - 2 alertes créées (1 visible patient, 1 masquée)')
            print(f'  - 2 recommandations créées (1 visible patient, 1 masquée)')
        
    except Exception as e:
        print(f'Erreur lors de la création: {e}')

if __name__ == '__main__':
    asyncio.run(create_test_data())
