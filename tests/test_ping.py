"""Tests Pytest pour vérifier le bon fonctionnement des endpoints basiques.
Tous les commentaires et la documentation sont rédigés en français.
"""

import pytest
from httpx import AsyncClient

from backend.main import app


@pytest.mark.asyncio
async def test_ping():
    """Vérifie que l'endpoint /ping répond 200 et le corps attendu."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
