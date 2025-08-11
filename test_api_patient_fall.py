#!/usr/bin/env python3
"""
Test direct de l'API pour le patient "fall"
"""
import requests
import json

def test_api_patient():
    base_url = "http://localhost:8000"
    
    print("=== TEST API PATIENT 'fall' ===")
    
    # 1. Connexion pour obtenir le token
    login_data = {
        "identifiant": "fall",
        "mot_de_passe": "123456"  # Mot de passe correct
    }
    
    print("1. Connexion...")
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        print(f"Statut connexion: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"Token obtenu: {token[:20]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 2. Test endpoint stats
            print("\n2. Test /stats...")
            stats_response = requests.get(f"{base_url}/stats", headers=headers)
            print(f"Statut /stats: {stats_response.status_code}")
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"Stats: {json.dumps(stats, indent=2)}")
            else:
                print(f"Erreur /stats: {stats_response.text}")
            
            # 3. Test endpoint alertes
            print("\n3. Test /alerts...")
            alerts_response = requests.get(f"{base_url}/alerts", headers=headers)
            print(f"Statut /alerts: {alerts_response.status_code}")
            if alerts_response.status_code == 200:
                alerts = alerts_response.json()
                print(f"Nombre d'alertes: {len(alerts)}")
                for i, alert in enumerate(alerts):
                    print(f"  Alerte {i+1}: {alert.get('message', 'N/A')} - {alert.get('niveau', 'N/A')}")
            else:
                print(f"Erreur /alerts: {alerts_response.text}")
            
            # 4. Test endpoint recommandations
            print("\n4. Test /recommendations...")
            reco_response = requests.get(f"{base_url}/recommendations", headers=headers)
            print(f"Statut /recommendations: {reco_response.status_code}")
            if reco_response.status_code == 200:
                recos = reco_response.json()
                print(f"Nombre de recommandations: {len(recos)}")
                for i, reco in enumerate(recos):
                    print(f"  Reco {i+1}: {reco.get('titre', 'N/A')}")
            else:
                print(f"Erreur /recommendations: {reco_response.text}")
            
            # 5. Test endpoint appareils
            print("\n5. Test /my/devices...")
            devices_response = requests.get(f"{base_url}/my/devices", headers=headers)
            print(f"Statut /my/devices: {devices_response.status_code}")
            if devices_response.status_code == 200:
                devices = devices_response.json()
                print(f"Nombre d'appareils: {len(devices)}")
                for i, device in enumerate(devices):
                    print(f"  Appareil {i+1}: {device.get('nom', device.get('type', 'N/A'))} - {device.get('numero_serie', 'N/A')}")
            else:
                print(f"Erreur /my/devices: {devices_response.text}")
                
        else:
            print(f"Erreur connexion: {response.text}")
            
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_api_patient()
