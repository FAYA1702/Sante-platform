#!/usr/bin/env python3
"""
Nettoyer les alertes orphelines du patient "fall"
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def clean_orphan_alerts():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== NETTOYAGE ALERTES ORPHELINES PATIENT 'fall' ===")
    
    # Trouver le patient "fall"
    patient = await db.utilisateurs.find_one({"username": "fall", "role": "patient"})
    
    if not patient:
        print("Patient 'fall' non trouvé!")
        return
    
    patient_id = str(patient["_id"])
    print(f"Patient trouvé: {patient['username']} ({patient_id})")
    
    # Vérifier les données de santé existantes
    donnees = await db.donnees.find({"user_id": patient_id}).to_list(None)
    print(f"Données de santé existantes: {len(donnees)}")
    
    # Vérifier les alertes existantes
    alertes = await db.alertes.find({"user_id": patient_id}).to_list(None)
    print(f"Alertes existantes: {len(alertes)}")
    
    if len(alertes) > 0:
        print("\nAlertes trouvées:")
        for i, alerte in enumerate(alertes, 1):
            print(f"  {i}. Message: {alerte.get('message', 'N/A')}")
            print(f"     Niveau: {alerte.get('niveau', 'N/A')}")
            print(f"     Date: {alerte.get('timestamp', 'N/A')}")
            print(f"     ID: {alerte.get('_id', 'N/A')}")
    
    # Si pas de données mais des alertes = alertes orphelines
    if len(donnees) == 0 and len(alertes) > 0:
        print(f"\n⚠️ ALERTES ORPHELINES DÉTECTÉES!")
        print(f"Le patient '{patient['username']}' a {len(alertes)} alertes mais 0 données de santé.")
        
        # Demander confirmation (simulation)
        print("\n🧹 Suppression des alertes orphelines...")
        
        # Supprimer toutes les alertes du patient
        result = await db.alertes.delete_many({"user_id": patient_id})
        print(f"Alertes supprimées: {result.deleted_count}")
        
        # Vérification
        alertes_restantes = await db.alertes.count_documents({"user_id": patient_id})
        print(f"Alertes restantes: {alertes_restantes}")
        
        if alertes_restantes == 0:
            print("✅ Nettoyage terminé avec succès!")
        else:
            print("❌ Erreur lors du nettoyage")
    
    elif len(donnees) > 0:
        print(f"\n✅ Pas de nettoyage nécessaire.")
        print(f"Le patient a {len(donnees)} données de santé et {len(alertes)} alertes.")
    
    else:
        print(f"\n✅ Aucune alerte à nettoyer.")
        print(f"Le patient n'a ni données ni alertes.")
    
    client.close()
    print("\nNettoyage terminé!")

if __name__ == "__main__":
    asyncio.run(clean_orphan_alerts())
