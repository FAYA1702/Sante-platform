#!/usr/bin/env python3
"""Script pour vérifier les alertes du patient fall et pourquoi kodia ne les voit pas."""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from backend.models.utilisateur import Utilisateur
from backend.models.alerte import Alerte
from backend.db import MONGO_URI, MONGO_DB_NAME

async def check_alerts():
    """Vérifie les alertes de fall et la logique de récupération pour kodia."""
    client = AsyncIOMotorClient(MONGO_URI)
    await init_beanie(database=client[MONGO_DB_NAME], document_models=[Utilisateur, Alerte])
    
    # Récupérer fall et kodia
    fall = await Utilisateur.find_one({"username": "fall"})
    kodia = await Utilisateur.find_one({"username": "kodia"})
    
    print("=== VERIFICATION DES ALERTES ===")
    
    if not fall or not kodia:
        print("Utilisateurs non trouves")
        return
    
    fall_id = str(fall.id)
    kodia_id = str(kodia.id)
    
    print(f"\nPATIENT fall ID: {fall_id}")
    print(f"MEDECIN kodia ID: {kodia_id}")
    
    # Récupérer toutes les alertes de fall
    db = client[MONGO_DB_NAME]
    alertes_fall = await db.alertes.find({"user_id": fall_id}).to_list(None)
    
    print(f"\nALERTES DE FALL (total: {len(alertes_fall)}):")
    for alerte in alertes_fall:
        print(f"  - ID: {alerte['_id']}")
        print(f"    Message: {alerte.get('message', 'N/A')}")
        print(f"    Niveau: {alerte.get('niveau', 'N/A')}")
        print(f"    Statut: {alerte.get('statut', 'N/A')}")
        print(f"    Date: {alerte.get('date', 'N/A')}")
        print()
    
    # Simuler la logique de récupération des alertes pour kodia
    print("SIMULATION LOGIQUE MEDECIN:")
    
    # 1. Récupérer les patients de kodia
    patients_cursor = db.utilisateurs.find({
        "role": "patient",
        "medecin_ids": kodia_id
    })
    patients_docs = await patients_cursor.to_list(None)
    
    print(f"Patients assignes a kodia: {len(patients_docs)}")
    for patient in patients_docs:
        print(f"  - {patient['username']} (ID: {patient['_id']})")
    
    if not patients_docs:
        print("PROBLEME: Aucun patient assigne a kodia!")
        return
    
    patient_ids = [str(doc["_id"]) for doc in patients_docs]
    print(f"Patient IDs pour filtrage: {patient_ids}")
    
    # 2. Récupérer les alertes "nouvelle" de ces patients
    alertes_nouvelles = await db.alertes.find({
        "user_id": {"$in": patient_ids},
        "statut": "nouvelle"
    }).to_list(None)
    
    print(f"\nALERTES 'nouvelle' pour kodia: {len(alertes_nouvelles)}")
    for alerte in alertes_nouvelles:
        print(f"  - {alerte.get('message', 'N/A')} (statut: {alerte.get('statut', 'N/A')})")
    
    # 3. Récupérer TOUTES les alertes de ces patients (tous statuts)
    alertes_toutes = await db.alertes.find({
        "user_id": {"$in": patient_ids}
    }).to_list(None)
    
    print(f"\nTOUTES LES ALERTES pour kodia: {len(alertes_toutes)}")
    for alerte in alertes_toutes:
        print(f"  - {alerte.get('message', 'N/A')} (statut: {alerte.get('statut', 'N/A')})")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_alerts())
