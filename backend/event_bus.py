"""Gestion simplifiée du bus d'événements Redis (asynchrone).

Si Redis n'est pas disponible (tests locaux, développement sans conteneur),
les publications sont ignorées avec un avertissement.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

try:
    import redis.asyncio as redis  # type: ignore
except ImportError:  # pragma: no cover
    redis = None  # type: ignore

LOGGER = logging.getLogger("event_bus")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
_redis_client: "redis.Redis | None" = None  # noqa: UP007


async def _get_client():
    """Retourne/initialise le client Redis asynchrone."""
    global _redis_client
    if redis is None:
        return None
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Redis non disponible : %s", exc)
            _redis_client = None
    return _redis_client


async def publish(channel: str, payload: Dict[str, Any]) -> None:  # noqa: D401
    """Publie *payload* (dict) sur le *channel* Redis.

    La sérialisation est effectuée en JSON. Les erreurs de connexion sont
    attrapées et enregistrées, afin de ne pas bloquer l’API.
    """

    client = await _get_client()
    if client is None:
        LOGGER.debug("Redis inactif : événement ignoré")
        return

    try:
        await client.publish(channel, json.dumps(payload, default=str))
    except Exception as exc:  # pragma: no cover
        LOGGER.warning("Échec publication Redis : %s", exc)
