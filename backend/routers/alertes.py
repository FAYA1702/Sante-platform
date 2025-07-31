"""Routeur pour la consultation des alertes."""

from typing import List

from fastapi import APIRouter, Depends

from backend.dependencies.auth import get_current_user


from backend.models.alerte import Alerte
from backend.schemas.alerte import AlerteEnDB

from fastapi.responses import StreamingResponse
import json

router = APIRouter()


@router.get("/alerts/stream", response_class=StreamingResponse)
async def stream_alertes():
    """Flux Server-Sent Events renvoyant chaque nouvelle alerte en temps réel."""
    async def event_generator():
        # utilise le change stream Mongo pour écouter les insertions
        async with Alerte.watch(full_document='updateLookup') as stream:
            async for change in stream:
                if change.get('operationType') != 'insert':
                    continue
                doc = change["fullDocument"]
                data = {
                    "id": str(doc["_id"]),
                    "message": doc["message"],
                    "niveau": doc["niveau"],
                    "date": doc["date"],
                }
                yield f"data:{json.dumps(data)}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/alerts", response_model=List[AlerteEnDB])
async def lister_alertes():
    """Liste toutes les alertes de la plateforme (Beanie)."""
    alertes_docs = await Alerte.find_all().to_list()
    return [AlerteEnDB(id=str(a.id), message=a.message, niveau=a.niveau, date=a.date) for a in alertes_docs]
