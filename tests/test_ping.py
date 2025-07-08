"""Tests Pytest pour vérifier le bon fonctionnement des endpoints basiques.
Tous les commentaires et la documentation sont rédigés en français.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app


@pytest.mark.asyncio
async def test_ping():
    """Vérifie que l'endpoint /ping répond 200 et le corps attendu."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
