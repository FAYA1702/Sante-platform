"""Tests Pytest pour l'authentification (inscription + connexion).

Exécute les endpoints /auth/register et /auth/login en utilisant un client MongoDB mocké grâce à `mongomock_motor`.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from unittest.mock import patch

from backend.models.utilisateur import Utilisateur
from backend.models.device import Device
from backend.models.donnee import Donnee
from backend.models.alerte import Alerte
from backend.models.recommandation import Recommandation


@pytest.mark.asyncio
async def test_inscription_et_connexion():
    """Teste l'inscription puis la connexion d'un utilisateur."""

    # Client MongoDB mocké en mémoire
    mock_client = AsyncMongoMockClient()

    # Initialiser Beanie sur la base mockée
    await init_beanie(
        database=mock_client["test_db"],
        document_models=[Utilisateur, Device, Donnee, Alerte, Recommandation],
    )

    # Patcher la fonction get_client puis importer l'application
    with patch("backend.db.get_client", return_value=mock_client):
        from backend.main import app  # import différé pour utiliser le client mocké

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Inscription
            payload_register = {
                "email": "testuser@example.com",
                "username": "testuser",
                "mot_de_passe": "motdepasse123",
            }
            resp = await client.post("/auth/register", json=payload_register)
            assert resp.status_code == 201
            assert resp.json()["access_token"]

            # Connexion via nom d'utilisateur
            payload_login_username = {
                "identifiant": "testuser",
                "mot_de_passe": "motdepasse123",
            }
            resp2 = await client.post("/auth/login", json=payload_login_username)
