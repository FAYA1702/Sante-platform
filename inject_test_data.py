#!/usr/bin/env python3
"""
Script d'injection de données de test pour générer des alertes et recommandations IA
"""
import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import redis.asyncio as redis

async def inject_test_data():
    try:
        # Connexion MongoDB
        client = AsyncIOMotorClient('mongodb://localhost:27017')
        db = client['sante_db']
        
        # Connexion Redis
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Récupérer un patient existant
        patient = await db.utilisateurs.find_one({'role': 'patient'})
        if not patient:
            print('Aucun patient trouvé')
            return
        
        patient_id = str(patient['_id'])
        username = patient.get('username', 'Patient inconnu')
        print(f'Patient trouvé: {username} (ID: {patient_id})')
        
        # Données de test critiques (tachycardie + hypoxie)
        test_data = [
            {
                'user_id': patient_id,
                'frequence_cardiaque': 125,  # Tachycardie
                'pression_arterielle': '140/90',
                'taux_oxygene': 89,  # Hypoxie critique
                'date': datetime.now(),
                'device_id': 'test_device_001',
                'source': 'Test IA'
            },
            {
                'user_id': patient_id,
                'frequence_cardiaque': 110,  # Tachycardie légère
                'pression_arterielle': '135/85',
                'taux_oxygene': 91,  # Hypoxie modérée
                'date': datetime.now(),
                'device_id': 'test_device_002',
                'source': 'Test IA'
            }
        ]
        
        for data in test_data:
            # Insérer dans MongoDB
            result = await db.donnees_sante.insert_one(data)
            print(f'Donnée insérée: {result.inserted_id}')
            
            # Publier dans Redis pour déclencher l'IA
            await redis_client.publish('health_data', json.dumps({
                'user_id': data['user_id'],
                'frequence_cardiaque': data['frequence_cardiaque'],
                'taux_oxygene': data['taux_oxygene'],
                'pression_arterielle': data['pression_arterielle'],
                'timestamp': data['date'].isoformat()
            }))
            print(f'Publié dans Redis pour user_id: {data["user_id"]}')
        
        await redis_client.close()
        client.close()
        print('✅ Injection terminée - L\'IA devrait générer des alertes et recommandations')
        
    except Exception as e:
        print(f'❌ Erreur lors de l\'injection: {e}')

if __name__ == '__main__':
    asyncio.run(inject_test_data())
