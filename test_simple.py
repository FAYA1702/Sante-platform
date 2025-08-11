#!/usr/bin/env python3
"""
Test simple de l'endpoint médecin sans emojis
"""
import requests
import json

def test_simple():
    base_url = "http://localhost:8000"
    
    # Connexion médecin - essayer différents mots de passe
    login_attempts = [
        {"identifiant": "faye", "mot_de_passe": "password123"},
        {"identifiant": "faye", "mot_de_passe": "medecin"},
        {"identifiant": "faye", "mot_de_passe": "123456"},
        {"identifiant": "medecin", "mot_de_passe": "medecin123"},
    ]
    
    try:
        print("=== TEST SIMPLE MEDECIN ===")
        
        # 1. Connexion - essayer plusieurs identifiants
        token = None
        for attempt in login_attempts:
            login_response = requests.post(f"{base_url}/auth/login", json=attempt)
            if login_response.status_code == 200:
                token = login_response.json().get("access_token")
                print(f"Connexion reussie avec: {attempt['identifiant']}")
                break
            else:
                print(f"Echec avec {attempt['identifiant']}: {login_response.status_code}")
        
        if not token:
            print("Aucune connexion reussie")
            return
        

        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Test recommandations médecin
        print("\nTest /medecin/recommandations...")
        recos_response = requests.get(f"{base_url}/medecin/recommandations?statut=nouvelle", headers=headers)
        print(f"Status: {recos_response.status_code}")
        
        if recos_response.status_code == 200:
            recos = recos_response.json()
            print(f"Recommandations trouvees: {len(recos)}")
            for reco in recos:
                print(f"  - {reco.get('titre', 'N/A')}")
        else:
            print(f"Erreur: {recos_response.text}")
        
        # 3. Test patients
        print("\nTest /medecin/patients...")
        patients_response = requests.get(f"{base_url}/medecin/patients", headers=headers)
        print(f"Status: {patients_response.status_code}")
        
        if patients_response.status_code == 200:
            patients = patients_response.json()
            print(f"Patients trouves: {len(patients)}")
        else:
            print(f"Erreur: {patients_response.text}")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == '__main__':
    test_simple()
