#!/usr/bin/env python3
"""
Script de migration pour ajouter le champ 'source' aux données de santé existantes.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def migrate_source_field():
    """Ajoute le champ source aux documents existants."""
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['sante_db']
    collection = db['donnees']
    
    print("Début de la migration du champ 'source'...")
    
    # Compter les documents sans champ source
    count_without_source = await collection.count_documents({'source': {'$exists': False}})
    print(f"Documents à migrer: {count_without_source}")
    
    if count_without_source == 0:
        print("Aucune migration nécessaire.")
        client.close()
        return
    
    # Mettre à jour tous les documents sans champ source
    result = await collection.update_many(
        {'source': {'$exists': False}},
        {'$set': {'source': 'saisie_manuelle'}}
    )
    
    print(f"Migration terminée: {result.modified_count} documents mis à jour")
    
    # Vérification
    count_with_source = await collection.count_documents({'source': {'$exists': True}})
    print(f"Total de documents avec champ source: {count_with_source}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_source_field())
