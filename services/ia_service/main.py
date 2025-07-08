"""Microservice IA/ML minimal.

- Écoute le canal Redis `nouvelle_donnee`.
- Récupère la donnée dans MongoDB.
- Applique des règles simples (ex : tachycardie > 100 bpm, hypoxie < 92 %).
- Insère une Alerte et publie un événement `notify`.

Ce service est volontairement succinct : il pourra être enrichi avec un vrai
modèle ML (scikit-learn, PyTorch, etc.).
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict

import motor.motor_asyncio
import redis.asyncio as redis  # type: ignore
from fastapi import FastAPI
from pydantic import BaseModel, Field

LOGGER = logging.getLogger("ia_service")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sante_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

ALERT_CHANNEL = "notify"
SOURCE_CHANNEL = "nouvelle_donnee"


class Alerte(BaseModel):
    utilisateur_id: str = Field(...)
    message: str = Field(...)
    niveau: str = Field(..., pattern="^(normal|warning|critical)$")
    date: str = Field(...)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise les clients Redis + Mongo et lance la tâche worker."""
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    db = mongo_client[MONGO_DB_NAME]

    async def worker():
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(SOURCE_CHANNEL)
        LOGGER.info("IA Service : abonné à %s", SOURCE_CHANNEL)
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                payload: Dict[str, Any] = json.loads(message["data"])
                await process_event(payload, db, redis_client)
            except Exception as exc:  # pragma: no cover
                LOGGER.exception("Erreur traitement IA: %s", exc)

    task = asyncio.create_task(worker())
    yield
    task.cancel()
    await mongo_client.close()
    await redis_client.close()


aapp = FastAPI(title="IA Service", lifespan=lifespan)  # noqa: N818 (alias évite conflit)


@aapp.get("/health", tags=["système"])
async def health():  # noqa: D401
    """Endpoint de liveness probe."""
    return {"status": "ok"}


async def process_event(payload: Dict[str, Any], db, redis_client) -> None:  # type: ignore
    """Analyse la nouvelle donnée puis crée une alerte si nécessaire."""
    donnee_id = payload.get("donnee_id")
    if not donnee_id:
        return

    donnee = await db["donnees"].find_one({"_id": {"$eq": {"$oid": donnee_id}}})
    if not donnee:
        return

    alerts: list[Alerte] = []
    fc = donnee.get("frequence_cardiaque")
    spo2 = donnee.get("taux_oxygene")

    if fc and fc > 100:
        alerts.append(
            Alerte(
                utilisateur_id=donnee["utilisateur_id"],
                message="Tachycardie détectée",
                niveau="warning",
                date=donnee["date"],
            )
        )
    if spo2 and spo2 < 92:
        alerts.append(
            Alerte(
                utilisateur_id=donnee["utilisateur_id"],
                message="Hypoxie détectée",
                niveau="critical",
                date=donnee["date"],
            )
        )

    for alerte in alerts:
        await db["alertes"].insert_one(alerte.model_dump())
        await redis_client.publish(ALERT_CHANNEL, alerte.model_dump_json())
        LOGGER.info("Alerte générée et publiée : %s", alerte.message)
