"""
Tests automatisés pour l'inscription avec différents rôles (patient, medecin, admin, technicien).
- Les rôles patient/medecin doivent réussir via /auth/register.
- Les rôles admin/technicien doivent échouer via /auth/register (400).
- Les rôles admin/technicien doivent réussir via /auth/register-admin si authentifié en admin.
"""
import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_inscription_patient_medecin():
    async with AsyncClient(app=app, base_url="http://test") as ac:
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
    async with AsyncClient(app=app, base_url="http://test") as ac:
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
    # Simule un admin déjà connecté (mock du décorateur verifier_roles)
    from backend.models.utilisateur import Role
    async def fake_verifier_roles(roles):
        class FakeUser:
            role = Role.admin
        return FakeUser()
    import backend.routers.auth as auth_router
    monkeypatch.setattr(auth_router, "verifier_roles", lambda roles: fake_verifier_roles)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        for role in ["admin", "technicien"]:
            resp = await ac.post("/auth/register-admin", json={
                "email": f"{role}3@exemple.com",
                "username": f"{role}3",
                "mot_de_passe": "motdepasse123",
                "role": role
            })
            assert resp.status_code == 201, f"Echec inscription admin/technicien par admin: {resp.text}"
            assert "access_token" in resp.json()
