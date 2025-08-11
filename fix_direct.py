#!/usr/bin/env python3
"""
Script de correction directe des assignations
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def fix_direct():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== CORRECTION DIRECTE ===")
    
    # IDs des utilisateurs (d'après le diagnostic)
    medecin_faye_id = "6888576a2f55329d625de8ed"
    medecin_talla_id = "68953ad1c9d4130633246ef2"
    patient_patient_id = "68884d1d74b0b31128156319"
    patient_mor_id = "68953aaac9d4130633246ef1"
    
    # 1. Assigner patient "mor" au médecin "talla"
    result1 = await db.utilisateurs.update_one(
        {"_id": ObjectId(patient_mor_id)},
        {"$set": {"medecin_ids": [medecin_talla_id]}}
    )
    print(f"Patient mor mis à jour: {result1.modified_count}")
    
    result2 = await db.utilisateurs.update_one(
        {"_id": ObjectId(medecin_talla_id)},
        {"$set": {"patient_ids": [patient_mor_id]}}
    )
    print(f"Médecin talla mis à jour: {result2.modified_count}")
    
    # 2. Corriger les statuts des recommandations
    result3 = await db.recommandations.update_many(
        {"statut": {"$exists": False}},
        {"$set": {"statut": "nouvelle"}}
    )
    print(f"Recommandations statut corrigé: {result3.modified_count}")
    
    result4 = await db.recommandations.update_many(
        {"statut": None},
        {"$set": {"statut": "nouvelle"}}
    )
    print(f"Recommandations statut null corrigé: {result4.modified_count}")
    
    # 3. Vérification finale
    print("\n=== VERIFICATION ===")
    
    # Vérifier les assignations
    patient_mor = await db.utilisateurs.find_one({"_id": ObjectId(patient_mor_id)})
    medecin_talla = await db.utilisateurs.find_one({"_id": ObjectId(medecin_talla_id)})
    
    print(f"Patient mor medecin_ids: {patient_mor.get('medecin_ids', [])}")
    print(f"Médecin talla patient_ids: {medecin_talla.get('patient_ids', [])}")
    
    # Vérifier les recommandations par patient
    recos_patient = await db.recommandations.count_documents({"user_id": patient_patient_id})
    recos_mor = await db.recommandations.count_documents({"user_id": patient_mor_id})
    
    print(f"Recommandations patient 'patient': {recos_patient}")
    print(f"Recommandations patient 'mor': {recos_mor}")
    
    # Vérifier les statuts
    recos_nouvelles = await db.recommandations.count_documents({"statut": "nouvelle"})
    print(f"Recommandations avec statut 'nouvelle': {recos_nouvelles}")
    
    client.close()
    print("Correction terminee")

if __name__ == "__main__":
    asyncio.run(fix_direct())
