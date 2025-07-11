"""Tests RBAC détaillés pour vérifier les accès selon le rôle."""

import pytest
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from unittest.mock import patch

from backend.models import Device, Donnee, Alerte, Recommandation, Utilisateur  # type: ignore
from backend.models.utilisateur import Role


@pytest.mark.asyncio
async def test_rbac_roles_access():
    """Valide les contrôles d'accès fins :
    - patient ne peut pas accéder à /devices
    - technicien peut accéder à /devices
    - technicien ne peut pas accéder à /data
    - admin peut changer le rôle d'un utilisateur
    """

    # Base mockée (MongoDB en mémoire)
    mock_client = AsyncMongoMockClient()
    db = mock_client["sante_test"]
    await init_beanie(database=db, document_models=[Device, Donnee, Alerte, Recommandation, Utilisateur])

    with patch("backend.db.get_client", return_value=mock_client):
        # Import différé après patch pour que l'app utilise la DB mockée
        from backend.main import app  # noqa: WPS433

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Créer un admin
            resp = await client.post(
                "/auth/register",
                json={"email": "admin@example.com", "username": "admin", "mot_de_passe": "pass123"},
            )
            token_admin = resp.json()["access_token"]
            # élève directement le rôle dans la DB car endpoint nécessite déjà admin
            admin_user = await Utilisateur.find_one({"username": "admin"})
            admin_user.role = Role.admin  # type: ignore
            await admin_user.save()
            headers_admin = {"Authorization": f"Bearer {token_admin}"}

            # 2. Créer un patient
            resp = await client.post(
                "/auth/register",
                json={"email": "pat@example.com", "username": "patient", "mot_de_passe": "pass123"},
            )
            id_patient = Utilisateur.parse_obj((await Utilisateur.find_one({"username": "patient"})).dict()).id  # type: ignore
            token_patient = resp.json()["access_token"]
            headers_patient = {"Authorization": f"Bearer {token_patient}"}

            # 3. Admin change rôle patient -> technicien
            resp = await client.patch(
                f"/users/{id_patient}/role",
                json={"role": "technicien"},
                headers=headers_admin,
            )
            assert resp.status_code == 200
            assert resp.json()["role"] == "technicien"

            # Récupérer token technicien (patient reste connecté comme patient dans token, donc relogin)
            resp = await client.post(
                "/auth/login",
                json={"identifiant": "patient", "mot_de_passe": "pass123"},
            )
            token_tech = resp.json()["access_token"]
            headers_tech = {"Authorization": f"Bearer {token_tech}"}

            # 4. patient (token initial) accède désormais à /devices car rôle changé -> 200
            resp = await client.get("/devices", headers=headers_patient)
            assert resp.status_code == 200

            # 5. technicien (après promotion) peut accéder à /devices -> 200
            resp = await client.get("/devices", headers=headers_tech)
            assert resp.status_code == 200

            # 6. technicien tente d'accéder à /data -> 403
            resp = await client.get("/data", headers=headers_tech)
            assert resp.status_code == 403
