import asyncio
import json
from datetime import datetime

import fakeredis.aioredis
import mongomock_motor
import pytest

from ia_service.main import process_event, FC_MAX, SPO2_MIN, ALERT_CHANNEL


@pytest.mark.asyncio
async def test_process_event_generates_alerts(monkeypatch):
    """Vérifie qu'une alerte est créée et publiée lorsque les seuils sont dépassés."""

    # --- DB mock ---
    client = mongomock_motor.AsyncMongoMockClient()
    db = client["test_db"]

    # Insère une donnée dépassant les deux seuils
    donnee = {
        "_id": mongomock_motor.ObjectId(),
        "utilisateur_id": "user123",
        "frequence_cardiaque": FC_MAX + 10,
        "taux_oxygene": SPO2_MIN - 2,
        "date": datetime.utcnow().isoformat(),
    }
    await db["donnees"].insert_one(donnee)

    # --- Redis mock ---
    redis_client = await fakeredis.aioredis.create_redis_pool()

    published = []

    async def fake_publish(channel, message):  # noqa: D401
        if channel == ALERT_CHANNEL:
            published.append(json.loads(message))
        return 1

    monkeypatch.setattr(redis_client, "publish", fake_publish)

    # --- Exécution ---
    await process_event({"donnee_id": str(donnee["_id"])}, db, redis_client)

    # --- Vérifications ---
    alerts_in_db = await db["alertes"].find().to_list(length=10)
    assert len(alerts_in_db) == 2  # tachycardie + hypoxie
    assert len(published) == 2

    # Vérifie contenu d'une alerte
    msg = {a["message"] for a in published}
    assert "Tachycardie détectée" in msg
    assert "Hypoxie détectée" in msg


@pytest.mark.asyncio
async def test_process_event_no_alert(monkeypatch):
    """Aucune alerte si les valeurs sont dans les limites."""

    client = mongomock_motor.AsyncMongoMockClient()
    db = client["test_db"]

    donnee = {
        "_id": mongomock_motor.ObjectId(),
        "utilisateur_id": "user123",
        "frequence_cardiaque": FC_MAX - 10,
        "taux_oxygene": SPO2_MIN + 1,
        "date": datetime.utcnow().isoformat(),
    }
    await db["donnees"].insert_one(donnee)

    redis_client = await fakeredis.aioredis.create_redis_pool()

    published = []

    async def fake_publish(channel, message):
        published.append(message)
        return 1

    monkeypatch.setattr(redis_client, "publish", fake_publish)

    await process_event({"donnee_id": str(donnee["_id"])}, db, redis_client)

    alerts_in_db = await db["alertes"].find().to_list(length=10)
    assert not alerts_in_db
    assert not published
