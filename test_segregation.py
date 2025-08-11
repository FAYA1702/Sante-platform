#!/usr/bin/env python3
"""
Test de la ségrégation des données par médecin
"""
import requests
import json

def test_medecin(username, password, expected_patients, expected_recos):
    """Test un médecin spécifique"""
    base_url = "http://localhost:8000"
    
    print(f"\n=== TEST MEDECIN {username.upper()} ===")
    
    # Connexion
    login_data = {"identifiant": username, "mot_de_passe": password}
    login_response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Echec connexion: {login_response.status_code}")
        return False
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Connexion réussie")
    
    # Test patients
    patients_response = requests.get(f"{base_url}/medecin/patients", headers=headers)
    if patients_response.status_code == 200:
        patients = patients_response.json()
        print(f"📋 Patients trouvés: {len(patients)} (attendu: {expected_patients})")
        for patient in patients:
            print(f"   - {patient.get('username', 'N/A')} ({patient.get('id', 'N/A')})")
        
        if len(patients) != expected_patients:
            print(f"❌ ERREUR: Nombre de patients incorrect!")
            return False
    else:
        print(f"❌ Erreur patients: {patients_response.status_code}")
        return False
    
    # Test recommandations
    recos_response = requests.get(f"{base_url}/medecin/recommandations?statut=nouvelle", headers=headers)
    if recos_response.status_code == 200:
        recos = recos_response.json()
        print(f"💊 Recommandations trouvées: {len(recos)} (attendu: {expected_recos})")
        for reco in recos:
            try:
                titre = reco.get('titre', 'N/A')
                patient_nom = reco.get('patient_nom', 'N/A')
                print(f"   - {patient_nom}: {titre[:50]}...")
            except UnicodeEncodeError:
                print(f"   - {reco.get('patient_nom', 'N/A')}: [Titre avec caractères spéciaux]")
        
        if len(recos) != expected_recos:
            print(f"❌ ERREUR: Nombre de recommandations incorrect!")
            return False
    else:
        print(f"❌ Erreur recommandations: {recos_response.status_code}")
        return False
    
    print(f"✅ Test {username} RÉUSSI")
    return True

def main():
    print("=== TEST SEGREGATION DONNEES PATIENT-MEDECIN ===")
    
    # Test médecin "faye" - doit voir 1 patient et ses recommandations
    success_faye = test_medecin("faye", "123456", expected_patients=1, expected_recos=3)
    
    # Test médecin "talla" - doit voir 1 patient et ses recommandations
    success_talla = test_medecin("talla", "medecin123", expected_patients=1, expected_recos=3)
    
    print(f"\n=== RESULTAT FINAL ===")
    print(f"Médecin faye: {'✅ RÉUSSI' if success_faye else '❌ ÉCHEC'}")
    print(f"Médecin talla: {'✅ RÉUSSI' if success_talla else '❌ ÉCHEC'}")
    
    if success_faye and success_talla:
        print("🎉 SEGREGATION PARFAITE: Chaque médecin voit uniquement ses patients et leurs données!")
    else:
        print("❌ PROBLEME DE SEGREGATION: Correction nécessaire")

if __name__ == "__main__":
    main()
