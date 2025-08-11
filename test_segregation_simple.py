#!/usr/bin/env python3
"""
Test simple de la ségrégation des données par médecin
"""
import requests

def test_medecin(username, password):
    """Test un médecin spécifique"""
    base_url = "http://localhost:8000"
    
    print(f"\n=== TEST MEDECIN {username.upper()} ===")
    
    # Connexion
    login_data = {"identifiant": username, "mot_de_passe": password}
    login_response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"Echec connexion: {login_response.status_code}")
        return None, None
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Connexion reussie")
    
    # Test patients
    patients_response = requests.get(f"{base_url}/medecin/patients", headers=headers)
    patients_count = 0
    if patients_response.status_code == 200:
        patients = patients_response.json()
        patients_count = len(patients)
        print(f"Patients trouves: {patients_count}")
        for patient in patients:
            print(f"  - {patient.get('username', 'N/A')}")
    else:
        print(f"Erreur patients: {patients_response.status_code}")
    
    # Test recommandations
    recos_response = requests.get(f"{base_url}/medecin/recommandations?statut=nouvelle", headers=headers)
    recos_count = 0
    if recos_response.status_code == 200:
        recos = recos_response.json()
        recos_count = len(recos)
        print(f"Recommandations trouvees: {recos_count}")
        for reco in recos:
            patient_nom = reco.get('patient_nom', 'N/A')
            print(f"  - Patient: {patient_nom}")
    else:
        print(f"Erreur recommandations: {recos_response.status_code}")
    
    return patients_count, recos_count

def main():
    print("=== TEST SEGREGATION DONNEES ===")
    
    # Test médecin "faye"
    faye_patients, faye_recos = test_medecin("faye", "123456")
    
    # Test médecin "talla" 
    talla_patients, talla_recos = test_medecin("talla", "talla123")
    
    print(f"\n=== RESULTAT ===")
    print(f"Medecin faye: {faye_patients} patients, {faye_recos} recommandations")
    print(f"Medecin talla: {talla_patients} patients, {talla_recos} recommandations")
    
    # Vérification de la ségrégation
    if faye_patients == 1 and talla_patients == 1:
        print("SEGREGATION PATIENTS: OK")
    else:
        print("SEGREGATION PATIENTS: PROBLEME")
    
    if faye_recos == 3 and talla_recos == 3:
        print("SEGREGATION RECOMMANDATIONS: OK")
    else:
        print("SEGREGATION RECOMMANDATIONS: PROBLEME")

if __name__ == "__main__":
    main()
