#!/usr/bin/env python3
"""
Script de test direct de l'endpoint /medecin/recommandations
"""
import requests
import json

def test_medecin_endpoint():
    # URL de l'API
    base_url = "http://localhost:8000"
    
    # 1. Se connecter comme médecin pour obtenir un token
    login_data = {
        "username": "faye",  # Médecin
        "password": "medecin123"
    }
    
    try:
        print("=== TEST ENDPOINT MÉDECIN ===")
        
        # Connexion
        print("1. Connexion médecin...")
        login_response = requests.post(f"{base_url}/auth/token", data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Échec connexion: {login_response.status_code}")
            print(f"Réponse: {login_response.text}")
            return
        
        token_data = login_response.json()
        token = token_data.get("access_token")
        print(f"✅ Connexion réussie, token obtenu")
        
        # Headers avec authentification
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 2. Tester l'endpoint /medecin/patients
        print("\n2. Test /medecin/patients...")
        patients_response = requests.get(f"{base_url}/medecin/patients", headers=headers)
        print(f"Status: {patients_response.status_code}")
        if patients_response.status_code == 200:
            patients = patients_response.json()
            print(f"✅ Patients trouvés: {len(patients)}")
            for patient in patients:
                print(f"  - {patient.get('username')} (ID: {patient.get('id')})")
        else:
            print(f"❌ Erreur: {patients_response.text}")
        
        # 3. Tester l'endpoint /medecin/recommandations
        print("\n3. Test /medecin/recommandations...")
        recos_response = requests.get(f"{base_url}/medecin/recommandations?statut=nouvelle", headers=headers)
        print(f"Status: {recos_response.status_code}")
        if recos_response.status_code == 200:
            recos = recos_response.json()
            print(f"✅ Recommandations trouvées: {len(recos)}")
            for reco in recos:
                print(f"  - {reco.get('titre')} (Patient: {reco.get('patient_nom')})")
        else:
            print(f"❌ Erreur: {recos_response.text}")
        
        # 4. Tester l'endpoint /medecin/alertes
        print("\n4. Test /medecin/alertes...")
        alertes_response = requests.get(f"{base_url}/medecin/alertes?statut=nouvelle", headers=headers)
        print(f"Status: {alertes_response.status_code}")
        if alertes_response.status_code == 200:
            alertes = alertes_response.json()
            print(f"✅ Alertes trouvées: {len(alertes)}")
            for alerte in alertes:
                print(f"  - {alerte.get('message')} (Patient: {alerte.get('patient_nom')})")
        else:
            print(f"❌ Erreur: {alertes_response.text}")
        
        print("\n=== TEST TERMINÉ ===")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == '__main__':
    test_medecin_endpoint()
