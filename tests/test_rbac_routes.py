"""Tests supplémentaires pour vérifier que les routes protégées nécessitent bien un JWT.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from unittest.mock import patch

from backend.models import Device, Donnee, Alerte, Recommandation, Utilisateur  # type: ignore
from backend.models.utilisateur import Role


@pytest.mark.asyncio
async def test_routes_protegees():
    """Accès autorisé avec JWT, refusé sans JWT."""

    # DB mockée
    mock_client = AsyncMongoMockClient()
    db = mock_client["sante_test"]
    await init_beanie(database=db, document_models=[Device, Donnee, Alerte, Recommandation, Utilisateur])

    with patch("backend.db.get_client", return_value=mock_client):
        from backend.main import app  # import différé après patch

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Inscrire utilisateur
            resp = await client.post(
                "/auth/register",
                json={"email": "user@example.com", "username": "user", "mot_de_passe": "pass123"},
            )
            token = resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Créer données de test via API protégées
            # 1. Ajouter appareil
            resp = await client.post(
                "/devices",
                json={"type": "oxymètre", "numero_serie": "ABC123"},
                headers=headers,
            )
            assert resp.status_code == 201
            device_id = resp.json()["id"]

            # 2. Ajouter donnée de santé
            resp = await client.post(
                "/data",
                json={
                    "device_id": device_id,
                    "frequence_cardiaque": 72,
                    "pression_arterielle": "120/80",
                    "taux_oxygene": 98,
                    "date": "2025-07-07T00:00:00Z",
                },
                headers=headers,
            )
            assert resp.status_code == 201

            # 3. Insertion d'une alerte directe (via modèle) pour simplifier
            await Alerte(message="Test", niveau="normal").insert()

            # Vérifier accès sans token -> 401
            for path in ["/devices", "/data", "/alerts"]:
                r = await client.get(path)
                assert r.status_code == 401

            # Vérifier accès avec token -> 200
            for path in ["/devices", "/data", "/alerts"]:
                r = await client.get(path, headers=headers)
                assert r.status_code == 200
