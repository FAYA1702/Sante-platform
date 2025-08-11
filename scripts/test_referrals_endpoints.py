#!/usr/bin/env python3
"""Script pour tester les différents endpoints referrals.
Tous les commentaires sont rédigés en français.
"""

import requests
import json

def test_referrals_endpoints():
    """Teste différentes variantes de l'endpoint referrals."""
    
    # Authentification
    login_data = {'identifiant': 'faye', 'mot_de_passe': '123456'}
    response = requests.post('http://localhost:8000/auth/login', json=login_data)
    
    if response.status_code != 200:
        print(f"Erreur authentification: {response.status_code}")
        return
    
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    print("=== TEST ENDPOINTS REFERRALS ===")
    print(f"Token obtenu: {token[:50]}...")
    
    # Test différentes variantes d'URL
    urls_to_test = [
        '/referrals',
        '/referrals/',
        '/api/referrals',
        '/api/referrals/',
        '/orientations',
        '/orientations/'
    ]
    
    for url in urls_to_test:
        try:
            r = requests.get(f'http://localhost:8000{url}', headers=headers)
            print(f'{url:15} -> Status: {r.status_code}')
            if r.status_code == 200:
                data = r.json()
                print(f"                -> Données: {len(data)} orientations")
                if data:
                    print(f"                -> Première orientation: {data[0].get('id', 'N/A')}")
        except Exception as e:
            print(f'{url:15} -> Erreur: {e}')
    
    print("\n=== VERIFICATION ENDPOINTS DISPONIBLES ===")
    # Test quelques endpoints connus pour vérifier que l'API fonctionne
    known_endpoints = ['/auth/login', '/departments', '/users']
    for url in known_endpoints:
        try:
            if url == '/auth/login':
                # Test sans auth pour login
                r = requests.post(f'http://localhost:8000{url}', json={'test': 'test'})
            else:
                # Test avec auth pour les autres
                r = requests.get(f'http://localhost:8000{url}', headers=headers)
            print(f'{url:15} -> Status: {r.status_code}')
        except Exception as e:
            print(f'{url:15} -> Erreur: {e}')

if __name__ == "__main__":
    test_referrals_endpoints()
