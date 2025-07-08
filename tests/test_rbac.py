"""Tests pour vérifier le fonctionnement du RBAC sur les routes protégées.
Tout est rédigé en français.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from unittest.mock import patch

from backend.models import Utilisateur  # type: ignore  # dynamic import ok
from backend.models.utilisateur import Role
from backend.models.device import Device
from backend.models.donnee import Donnee
from backend.models.alerte import Alerte
from backend.models.recommandation import Recommandation


@pytest.mark.asyncio
async def test_rbac():
    """Vérifie l'accès aux routes protégées selon le rôle utilisateur."""

    # Client Mongo mocké en mémoire
    mock_client = AsyncMongoMockClient()
    db = mock_client["sante_test"]
    await init_beanie(database=db, document_models=[Device, Donnee, Alerte, Recommandation, Utilisateur])

    with patch("backend.db.get_client", return_value=mock_client):
        from backend.main import app  # import différé pour utiliser le client mocké

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Inscription d'un patient
            payload_register = {
                "email": "patient@example.com",
                "username": "patient",
                "mot_de_passe": "secret123",
            }
            resp = await client.post("/auth/register", json=payload_register)
            assert resp.status_code == 201

            # 2. Connexion pour récupérer le token
            payload_login = {"identifiant": "patient", "mot_de_passe": "secret123"}
            resp = await client.post("/auth/login", json=payload_login)
            token = resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # 3. Accès profil OK
            resp = await client.get("/protected/profile", headers=headers)
            assert resp.status_code == 200
            assert resp.json()["role"] == Role.patient

            # 4. Accès admin interdit pour patient
            resp = await client.get("/protected/admin", headers=headers)
            assert resp.status_code == 403

            # 5. Promotion utilisateur en admin dans la DB
            user = await Utilisateur.find_one({"username": "patient"})
            user.role = Role.admin
            await user.save()

            # 6. Nouvelle connexion pour nouveau token avec rôle admin
            resp = await client.post("/auth/login", json=payload_login)
            token_admin = resp.json()["access_token"]
            headers_admin = {"Authorization": f"Bearer {token_admin}"}

            # 7. Accès admin autorisé
            resp = await client.get("/protected/admin", headers=headers_admin)
            assert resp.status_code == 200
            assert resp.json()["message"] == "Bienvenue, administrateur."
