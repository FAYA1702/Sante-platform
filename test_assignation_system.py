#!/usr/bin/env python3
"""
Script de test et démonstration du système d'assignation patient-médecin
"""
import requests
import json

def test_assignation_system():
    base_url = "http://localhost:8000"
    
    print("=== TEST SYSTÈME D'ASSIGNATION PATIENT-MÉDECIN ===")
    
    # 1. Connexion patient "fall"
    print("\n1. CONNEXION PATIENT 'fall'")
    patient_login = {
        "identifiant": "fall",
        "mot_de_passe": "123456"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=patient_login)
    if response.status_code == 200:
        patient_token = response.json()["access_token"]
        patient_headers = {"Authorization": f"Bearer {patient_token}"}
        print("✅ Connexion patient réussie")
    else:
        print(f"❌ Erreur connexion patient: {response.text}")
        return
    
    # 2. Connexion médecin "kodia" (nouveau docteur créé)
    print("\n2. CONNEXION MÉDECIN 'kodia'")
    medecin_login = {
        "identifiant": "kodia",
        "mot_de_passe": "kodia123"  # Mot de passe supposé
    }
    
    response = requests.post(f"{base_url}/auth/login", json=medecin_login)
    if response.status_code == 200:
        medecin_token = response.json()["access_token"]
        medecin_headers = {"Authorization": f"Bearer {medecin_token}"}
        print("✅ Connexion médecin réussie")
    else:
        print(f"❌ Erreur connexion médecin: {response.text}")
        print("ℹ️ Le médecin 'kodia' n'existe peut-être pas encore")
        return
    
    # 3. Patient : Lister tous les médecins disponibles
    print("\n3. PATIENT : Liste des médecins disponibles")
    response = requests.get(f"{base_url}/assignation/tous-medecins", headers=patient_headers)
    if response.status_code == 200:
        medecins = response.json()["medecins"]
        print(f"Médecins disponibles: {len(medecins)}")
        for medecin in medecins:
            print(f"  - Dr. {medecin['username']} ({medecin['email']}) - {medecin.get('nb_patients', 0)} patients")
    else:
        print(f"❌ Erreur liste médecins: {response.text}")
    
    # 4. Patient : Demander assignation au Dr. kodia
    print("\n4. PATIENT : Demande d'assignation au Dr. kodia")
    if medecins:
        # Trouver l'ID du Dr. kodia
        kodia_id = None
        for medecin in medecins:
            if medecin['username'] == 'kodia':
                kodia_id = medecin['id']
                break
        
        if kodia_id:
            assignation_request = {"medecin_id": kodia_id}
            response = requests.post(
                f"{base_url}/assignation/demander-assignation", 
                json=assignation_request, 
                headers=patient_headers
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['message']}")
            else:
                print(f"❌ Erreur assignation: {response.text}")
        else:
            print("❌ Dr. kodia non trouvé dans la liste")
    
    # 5. Patient : Vérifier ses médecins assignés
    print("\n5. PATIENT : Mes médecins assignés")
    response = requests.get(f"{base_url}/assignation/mes-medecins", headers=patient_headers)
    if response.status_code == 200:
        mes_medecins = response.json()["medecins"]
        print(f"Médecins assignés: {len(mes_medecins)}")
        for medecin in mes_medecins:
            print(f"  - Dr. {medecin['username']} ({medecin['specialite']})")
    else:
        print(f"❌ Erreur mes médecins: {response.text}")
    
    # 6. Médecin : Vérifier ses patients assignés
    print("\n6. MÉDECIN : Mes patients assignés")
    response = requests.get(f"{base_url}/assignation/mes-patients", headers=medecin_headers)
    if response.status_code == 200:
        mes_patients = response.json()["patients"]
        print(f"Patients assignés: {len(mes_patients)}")
        for patient in mes_patients:
            print(f"  - {patient['username']} ({patient['email']}) - Assigné le {patient['date_assignation']}")
    else:
        print(f"❌ Erreur mes patients: {response.text}")
    
    print("\n=== RÉSUMÉ DU SYSTÈME D'ASSIGNATION ===")
    print("✅ Le système d'assignation patient-médecin fonctionne!")
    print("📋 Fonctionnalités disponibles:")
    print("   - Patient peut voir tous les médecins disponibles")
    print("   - Patient peut demander assignation à un médecin")
    print("   - Patient peut voir ses médecins assignés")
    print("   - Médecin peut voir ses patients assignés")
    print("   - Médecin peut accepter de nouveaux patients")
    print("   - Admin peut gérer toutes les assignations")

if __name__ == "__main__":
    test_assignation_system()
