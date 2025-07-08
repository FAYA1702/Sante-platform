"""Microservice Notifications.

Écoute le canal Redis `notify` et simule l'envoi d'alertes (courriel/SMS).
Pour l'instant, il écrit simplement dans les logs.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager

import redis.asyncio as redis  # type: ignore
from fastapi import FastAPI

LOGGER = logging.getLogger("notification_service")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
CHANNEL = "notify"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise le client Redis et lance le consumer."""
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)

    async def worker():
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(CHANNEL)
        LOGGER.info("Notification Service : abonné à %s", CHANNEL)
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                payload = json.loads(message["data"])
                await handle_notification(payload)
            except Exception as exc:  # pragma: no cover
                LOGGER.exception("Erreur notification : %s", exc)

    task = asyncio.create_task(worker())
    yield
    task.cancel()
    await redis_client.close()


app = FastAPI(title="Notification Service", lifespan=lifespan)


@app.get("/health", tags=["système"])
async def health():  # noqa: D401
    """Probe de liveness."""
    return {"status": "ok"}


async def handle_notification(payload):  # type: ignore
    """Simule l'envoi de notification (pour l'instant, log)."""
    utilisateur_id = payload.get("utilisateur_id", "inconnu")
    message = payload.get("message", "")
    LOGGER.info("[NOTIFY] Utilisateur %s: %s", utilisateur_id, message)
