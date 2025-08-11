#!/usr/bin/env python3
"""
Diagnostic des données existantes pour le patient "fall"
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def check_patient_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== DIAGNOSTIC DONNÉES PATIENT 'fall' ===")
    
    # Trouver le patient "fall"
    patient = await db.utilisateurs.find_one({"username": "fall", "role": "patient"})
    
    if not patient:
        print("Patient 'fall' non trouvé!")
        return
    
    patient_id = str(patient["_id"])
    print(f"Patient trouvé: {patient['username']} ({patient_id})")
    print(f"Email: {patient.get('email', 'N/A')}")
    print(f"Créé le: {patient.get('created_at', 'N/A')}")
    
    print("\n" + "="*50)
    
    # Vérifier les données de santé
    print("DONNEES DE SANTE:")
    donnees = await db.donnees.find({"user_id": patient_id}).to_list(None)
    print(f"Nombre de données: {len(donnees)}")
    
    for i, donnee in enumerate(donnees, 1):
        print(f"  {i}. Date: {donnee.get('timestamp', 'N/A')}")
        print(f"     FC: {donnee.get('frequence_cardiaque', 'N/A')} bpm")
        print(f"     PA: {donnee.get('pression_arterielle', 'N/A')}")
        print(f"     O2: {donnee.get('taux_oxygene', 'N/A')}%")
        print(f"     Device: {donnee.get('device_id', 'N/A')}")
        print(f"     Créé: {donnee.get('created_at', 'N/A')}")
        print()
    
    print("="*50)
    
    # Vérifier les alertes
    print("ALERTES:")
    alertes = await db.alertes.find({"user_id": patient_id}).to_list(None)
    print(f"Nombre d'alertes: {len(alertes)}")
    
    for i, alerte in enumerate(alertes, 1):
        print(f"  {i}. Message: {alerte.get('message', 'N/A')}")
        print(f"     Niveau: {alerte.get('niveau', 'N/A')}")
        print(f"     Statut: {alerte.get('statut', 'N/A')}")
        print(f"     Date: {alerte.get('timestamp', 'N/A')}")
        print(f"     Créé: {alerte.get('created_at', 'N/A')}")
        print()
    
    print("="*50)
    
    # Vérifier les recommandations
    print("RECOMMANDATIONS:")
    recommandations = await db.recommandations.find({"user_id": patient_id}).to_list(None)
    print(f"Nombre de recommandations: {len(recommandations)}")
    
    for i, reco in enumerate(recommandations, 1):
        print(f"  {i}. Titre: {reco.get('titre', 'N/A')}")
        print(f"     Description: {reco.get('description', 'N/A')}")
        print(f"     Contenu: {reco.get('contenu', 'N/A')[:100]}...")
        print(f"     Date: {reco.get('timestamp', 'N/A')}")
        print(f"     Créé: {reco.get('created_at', 'N/A')}")
        print()
    
    print("="*50)
    
    # Vérifier les appareils
    print("APPAREILS:")
    appareils = await db.appareils.find({"user_id": patient_id}).to_list(None)
    print(f"Nombre d'appareils: {len(appareils)}")
    
    for i, appareil in enumerate(appareils, 1):
        print(f"  {i}. Nom: {appareil.get('nom', appareil.get('type', 'N/A'))}")
        print(f"     Type: {appareil.get('type', 'N/A')}")
        print(f"     Série: {appareil.get('numero_serie', 'N/A')}")
        print(f"     Statut: {appareil.get('statut', 'N/A')}")
        print(f"     Créé: {appareil.get('created_at', 'N/A')}")
        print()
    
    client.close()
    print("Diagnostic terminé!")

if __name__ == "__main__":
    asyncio.run(check_patient_data())
