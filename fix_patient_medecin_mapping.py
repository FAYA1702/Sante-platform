#!/usr/bin/env python3
"""
Script pour corriger les assignations patient-médecin et garantir la ségrégation des données
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def fix_assignations():
    # Connexion MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== CORRECTION ASSIGNATIONS PATIENT-MEDECIN ===")
    
    # 1. Récupérer tous les utilisateurs
    medecins_cursor = db.utilisateurs.find({"role": "medecin"})
    medecins = await medecins_cursor.to_list(None)
    
    patients_cursor = db.utilisateurs.find({"role": "patient"})
    patients = await patients_cursor.to_list(None)
    
    print(f"Médecins trouvés: {len(medecins)}")
    print(f"Patients trouvés: {len(patients)}")
    
    # 2. Plan d'assignation logique
    # - Patient "patient" -> Médecin "faye" (déjà fait)
    # - Patient "mor" -> Médecin "talla" (nouveau)
    
    medecin_faye = None
    medecin_talla = None
    patient_patient = None
    patient_mor = None
    
    for medecin in medecins:
        if medecin["username"] == "faye":
            medecin_faye = medecin
        elif medecin["username"] == "talla":
            medecin_talla = medecin
    
    for patient in patients:
        if patient["username"] == "patient":
            patient_patient = patient
        elif patient["username"] == "mor":
            patient_mor = patient
    
    print(f"\nMédecin faye: {medecin_faye['_id'] if medecin_faye else 'NON TROUVÉ'}")
    print(f"Médecin talla: {medecin_talla['_id'] if medecin_talla else 'NON TROUVÉ'}")
    print(f"Patient patient: {patient_patient['_id'] if patient_patient else 'NON TROUVÉ'}")
    print(f"Patient mor: {patient_mor['_id'] if patient_mor else 'NON TROUVÉ'}")
    
    if not all([medecin_faye, medecin_talla, patient_patient, patient_mor]):
        print("❌ Utilisateurs manquants, impossible de continuer")
        return
    
    # 3. Corriger les assignations
    
    # Patient "patient" -> Médecin "faye" (vérifier/corriger)
    faye_id = str(medecin_faye["_id"])
    patient_id = str(patient_patient["_id"])
    
    await db.utilisateurs.update_one(
        {"_id": patient_patient["_id"]},
        {"$set": {"medecin_ids": [faye_id]}}
    )
    
    await db.utilisateurs.update_one(
        {"_id": medecin_faye["_id"]},
        {"$set": {"patient_ids": [patient_id]}}
    )
    
    print(f"✅ Patient 'patient' assigné au médecin 'faye'")
    
    # Patient "mor" -> Médecin "talla" (nouveau)
    talla_id = str(medecin_talla["_id"])
    mor_id = str(patient_mor["_id"])
    
    await db.utilisateurs.update_one(
        {"_id": patient_mor["_id"]},
        {"$set": {"medecin_ids": [talla_id]}}
    )
    
    await db.utilisateurs.update_one(
        {"_id": medecin_talla["_id"]},
        {"$set": {"patient_ids": [mor_id]}}
    )
    
    print(f"✅ Patient 'mor' assigné au médecin 'talla'")
    
    # 4. Vérifier le résultat
    print("\n=== VERIFICATION ASSIGNATIONS ===")
    
    medecins_updated = await db.utilisateurs.find({"role": "medecin"}).to_list(None)
    patients_updated = await db.utilisateurs.find({"role": "patient"}).to_list(None)
    
    for medecin in medecins_updated:
        print(f"Médecin {medecin['username']}: {len(medecin.get('patient_ids', []))} patients")
        for pid in medecin.get('patient_ids', []):
            patient_name = next((p['username'] for p in patients_updated if str(p['_id']) == pid), 'INCONNU')
            print(f"  - {patient_name} ({pid})")
    
    for patient in patients_updated:
        print(f"Patient {patient['username']}: {len(patient.get('medecin_ids', []))} médecins")
        for mid in patient.get('medecin_ids', []):
            medecin_name = next((m['username'] for m in medecins_updated if str(m['_id']) == mid), 'INCONNU')
            print(f"  - {medecin_name} ({mid})")
    
    # 5. Vérifier la répartition des recommandations
    print("\n=== VERIFICATION RECOMMANDATIONS ===")
    
    for patient in patients_updated:
        patient_id_str = str(patient["_id"])
        recos_count = await db.recommandations.count_documents({"user_id": patient_id_str})
        print(f"Patient {patient['username']} ({patient_id_str}): {recos_count} recommandations")
    
    client.close()
    print("\n✅ Correction terminée !")

if __name__ == "__main__":
    asyncio.run(fix_assignations())
