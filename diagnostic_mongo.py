#!/usr/bin/env python3
"""
Script de diagnostic MongoDB pour comprendre le problème des recommandations médecin
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def diagnostic():
    # Connexion MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sante_db"]
    
    print("=== DIAGNOSTIC MONGODB ===")
    
    # 1. Vérifier les recommandations
    print("\n1. RECOMMANDATIONS:")
    recos_cursor = db.recommandations.find({})
    recos = await recos_cursor.to_list(None)
    print(f"Total recommandations: {len(recos)}")
    
    for reco in recos[:3]:  # Afficher les 3 premières
        print(f"  - ID: {reco['_id']}")
        print(f"    User ID: {reco.get('user_id', 'MANQUANT')}")
        print(f"    Statut: {reco.get('statut', 'VIDE')}")
        titre = reco.get('titre', 'N/A')
        try:
            print(f"    Titre: {titre}")
        except UnicodeEncodeError:
            print(f"    Titre: [Contient des caractères spéciaux]")
        print(f"    Date: {reco.get('date', 'N/A')}")
        print()
    
    # 2. Vérifier les médecins
    print("\n2. MEDECINS:")
    medecins_cursor = db.utilisateurs.find({"role": "medecin"})
    medecins = await medecins_cursor.to_list(None)
    print(f"Total médecins: {len(medecins)}")
    
    for medecin in medecins:
        print(f"  - Username: {medecin['username']}")
        print(f"    ID: {medecin['_id']}")
        print(f"    Patient IDs: {medecin.get('patient_ids', [])}")
        print()
    
    # 3. Vérifier les patients
    print("\n3. PATIENTS:")
    patients_cursor = db.utilisateurs.find({"role": "patient"})
    patients = await patients_cursor.to_list(None)
    print(f"Total patients: {len(patients)}")
    
    for patient in patients:
        print(f"  - Username: {patient['username']}")
        print(f"    ID: {patient['_id']}")
        print(f"    Médecin IDs: {patient.get('medecin_ids', [])}")
        print()
    
    # 4. Vérifier les statuts des recommandations
    print("\n4. STATUTS RECOMMANDATIONS:")
    statuts = await db.recommandations.distinct("statut")
    print(f"Statuts existants: {statuts}")
    
    for statut in statuts:
        count = await db.recommandations.count_documents({"statut": statut})
        print(f"  - {statut}: {count} recommandations")
    
    # 5. Test de la requête médecin
    print("\n5. TEST REQUETE MEDECIN:")
    
    # Simuler la requête de l'endpoint médecin
    medecin_faye = await db.utilisateurs.find_one({"username": "faye", "role": "medecin"})
    if medecin_faye:
        medecin_id_str = str(medecin_faye["_id"])
        print(f"Médecin faye ID: {medecin_id_str}")
        
        # Récupérer ses patients
        patients_cursor = db.utilisateurs.find({
            "role": "patient",
            "medecin_ids": medecin_id_str
        })
        patients_docs = await patients_cursor.to_list(None)
        patient_ids = [str(doc["_id"]) for doc in patients_docs]
        print(f"Patients assignés: {len(patients_docs)} -> IDs: {patient_ids}")
        
        # Chercher les recommandations avec statut "nouvelle"
        query = {
            "user_id": {"$in": patient_ids},
            "statut": "nouvelle"
        }
        print(f"Requête: {query}")
        
        recos_cursor = db.recommandations.find(query)
        recos_docs = await recos_cursor.to_list(None)
        print(f"Recommandations trouvées: {len(recos_docs)}")
        
        # Essayer sans filtre de statut
        query_all = {"user_id": {"$in": patient_ids}}
        print(f"Requête sans statut: {query_all}")
        
        recos_all_cursor = db.recommandations.find(query_all)
        recos_all_docs = await recos_all_cursor.to_list(None)
        print(f"Recommandations (tous statuts): {len(recos_all_docs)}")
        
        for reco in recos_all_docs:
            print(f"  - Statut: '{reco.get('statut', 'VIDE')}', User: {reco.get('user_id')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(diagnostic())
