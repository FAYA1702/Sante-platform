"""Tests Pytest pour l'authentification (inscription et connexion).
Tout est rédigé en français.
"""

import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_inscription_et_connexion():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Inscription
        donnees = {
            "email": "testuser@example.com",
            "username": "testuser",
            "mot_de_passe": "motdepasse123"
        }
        resp = await ac.post("/register", json=donnees)
        assert resp.status_code == 201
        token = resp.json()["access_token"]
        assert token

        # Connexion avec username
        login = {"identifiant": "testuser", "mot_de_passe": "motdepasse123"}
        resp2 = await ac.post("/login", json=login)
        assert resp2.status_code == 200
        assert resp2.json()["access_token"]

        # Connexion avec email
        login2 = {"identifiant": "testuser@example.com", "mot_de_passe": "motdepasse123"}
        resp3 = await ac.post("/login", json=login2)
        assert resp3.status_code == 200
        assert resp3.json()["access_token"]
