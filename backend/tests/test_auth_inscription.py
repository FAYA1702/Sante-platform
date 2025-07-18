"""
Tests automatisés pour l'inscription avec différents rôles (patient, medecin, admin, technicien).
- Les rôles patient/medecin doivent réussir via /auth/register.
- Les rôles admin/technicien doivent échouer via /auth/register (400).
- Les rôles admin/technicien doivent réussir via /auth/register-admin si authentifié en admin.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient
from beanie import init_beanie
from unittest.mock import patch

from backend.models.utilisateur import Utilisateur, Role
from backend.models.device import Device
from backend.models.donnee import Donnee
from backend.models.alerte import Alerte
from backend.models.recommandation import Recommandation

async def build_test_client():
    """Construit un AsyncClient avec base Mongo mockée."""
    mock_client = AsyncMongoMockClient()
    await init_beanie(
        database=mock_client["test_db"],
        document_models=[Utilisateur, Device, Donnee, Alerte, Recommandation],
    )
    with patch("backend.db.get_client", return_value=mock_client):
        from backend.main import app as fastapi_app
        transport = ASGITransport(app=fastapi_app)
        client = AsyncClient(transport=transport, base_url="http://test")
        return fastapi_app, client


@pytest.mark.asyncio
async def test_inscription_patient_medecin():
    app, ac = await build_test_client()
    async with ac:
        for role in ["patient", "medecin"]:
            resp = await ac.post("/auth/register", json={
                "email": f"{role}1@exemple.com",
                "username": f"{role}1",
                "mot_de_passe": "motdepasse123",
                "role": role
            })
            assert resp.status_code == 201, f"Echec inscription {role}: {resp.text}"
            assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_inscription_admin_technicien_refuse():
    app, ac = await build_test_client()
    async with ac:
        for role in ["admin", "technicien"]:
            resp = await ac.post("/auth/register", json={
                "email": f"{role}2@exemple.com",
                "username": f"{role}2",
                "mot_de_passe": "motdepasse123",
                "role": role
            })
            assert resp.status_code == 400, f"Inscription {role} ne doit pas être acceptée: {resp.text}"


@pytest.mark.asyncio
async def test_inscription_admin_technicien_admin_ok(monkeypatch):
    app, ac = await build_test_client()
    # Patch verifier_roles pour toujours renvoyer un utilisateur admin
    import backend.routers.auth as auth_router
    from fastapi.security import HTTPBearer

    async def override_dep():
        class FakeUser:
            role = Role.admin
        return FakeUser()

    # Patch la dépendance de rôle ET get_current_user pour bypass JWT
    auth_router.verifier_roles = lambda roles: override_dep

    import backend.dependencies.auth as auth_dep
    from beanie.odm.fields import PydanticObjectId
    fake_oid = str(PydanticObjectId())
    async def fake_get_current_user(*args, **kwargs):
        class FakeUser:
            role = Role.admin
            id = fake_oid
        return FakeUser()
    auth_dep.get_current_user = fake_get_current_user
    auth_dep.verifier_jwt = lambda token: {"sub": fake_oid, "role": "admin"}

    # Insère un fake admin en base pour que get_current_user le retrouve
    from backend.routers.auth import hacher_mot_de_passe
    hash_admin = hacher_mot_de_passe("motdepasse123")
    await Utilisateur(id=fake_oid, email="admin@exemple.com", username="admin", mot_de_passe_hache=hash_admin, role=Role.admin).insert()

    async with ac:
        for role in ["admin", "technicien"]:
            resp = await ac.post(
                "/auth/register-admin",
                json={
                    "email": f"{role}3@exemple.com",
                    "username": f"{role}3",
                    "mot_de_passe": "motdepasse123",
                    "role": role
                },
                headers={"Authorization": "Bearer faketoken"}
            )
            assert resp.status_code == 201, f"Echec inscription admin/technicien par admin: {resp.text}"
            assert "access_token" in resp.json()
