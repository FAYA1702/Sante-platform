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
    import asyncio
    import redis.asyncio as redis
    import os
    
    async def event_generator():
        redis_client = None
        try:
            # Connexion Redis pour écouter les nouvelles alertes
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            redis_client = redis.from_url(redis_url)
            
            # Envoyer un heartbeat initial
            yield "data: {\"type\": \"heartbeat\", \"timestamp\": \"" + str(asyncio.get_event_loop().time()) + "\"}\n\n"
            
            # S'abonner au canal Redis pour les nouvelles alertes
            pubsub = redis_client.pubsub()
            await pubsub.subscribe('nouvelle_alerte')
            
            # Boucle infinie pour maintenir la connexion SSE
            while True:
                try:
                    # Écouter les messages Redis avec timeout
                    message = await asyncio.wait_for(pubsub.get_message(ignore_subscribe_messages=True), timeout=30.0)
                    
                    if message and message['type'] == 'message':
                        try:
                            # Parser le message JSON de l'alerte
                            alert_data = json.loads(message['data'])
                            
                            # Récupérer l'alerte complète depuis MongoDB
                            alerte = await Alerte.get(alert_data['alerte_id'])
                            if alerte:
                                data = {
                                    "type": "alert",
                                    "id": str(alerte.id),
                                    "user_id": alerte.user_id,
                                    "message": alerte.message,
                                    "niveau": alerte.niveau,
                                    "date": alerte.date.isoformat() if hasattr(alerte.date, 'isoformat') else str(alerte.date),
                                }
                                yield f"data: {json.dumps(data)}\n\n"
                        except json.JSONDecodeError:
                            # Ignorer les messages mal formés
                            continue
                        except Exception as e:
                            print(f"Erreur traitement message Redis: {e}")
                            continue
                    
                except asyncio.TimeoutError:
                    # Envoyer un heartbeat après timeout (toutes les 30 secondes)
                    yield "data: {\"type\": \"heartbeat\", \"timestamp\": \"" + str(asyncio.get_event_loop().time()) + "\"}\n\n"
                    continue
                    
                except asyncio.CancelledError:
                    # Connexion fermée côté client
                    break
                        
            # Nettoyage final
            try:
                await pubsub.unsubscribe('nouvelle_alerte')
                await pubsub.close()
            except Exception:
                pass
                
        except Exception as e:
            # En cas d'erreur, envoyer un message d'erreur et fermer proprement
            error_data = {
                "type": "error",
                "message": f"Erreur de streaming: {str(e)}"
            }
            yield f"data: {json.dumps(error_data)}\n\n"
        finally:
            if redis_client:
                try:
                    await redis_client.close()
                except Exception:
                    pass
            
    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.get("/alerts", response_model=List[AlerteEnDB])
async def lister_alertes(current_user=Depends(get_current_user)):
    """Liste les alertes de l'utilisateur connecté uniquement (sécurité RGPD)."""
    # Filtrer par user_id pour respecter la ségrégation des données
    alertes_docs = await Alerte.find({"user_id": str(current_user.id)}).to_list()
    return [AlerteEnDB(
        id=str(a.id), 
        user_id=a.user_id, 
        message=a.message, 
        niveau=a.niveau, 
        date=a.date
    ) for a in alertes_docs]


@router.patch("/alertes/{alerte_id}/marquer-vue")
async def marquer_alerte_vue(alerte_id: str, current_user=Depends(get_current_user)):
    """Marque une alerte comme vue par l'utilisateur connecté."""
    from fastapi import HTTPException
    from bson import ObjectId
    from datetime import datetime
    from backend.models.utilisateur import Utilisateur, Role
    
    try:
        alerte = await Alerte.find_one(Alerte.id == ObjectId(alerte_id))
        if not alerte:
            raise HTTPException(status_code=404, detail="Alerte introuvable")
        
        # Vérifier les permissions selon le rôle
        if current_user.role == Role.medecin:
            # Pour un médecin : vérifier que le patient lui est assigné
            patient = await Utilisateur.find_one(Utilisateur.id == ObjectId(alerte.user_id))
            if not patient or str(current_user.id) not in patient.medecin_ids:
                raise HTTPException(status_code=403, detail="Patient non assigné à ce médecin")
        elif current_user.role == Role.patient:
            # Pour un patient : vérifier que c'est sa propre alerte
            if alerte.user_id != str(current_user.id):
                raise HTTPException(status_code=403, detail="Accès non autorisé à cette alerte")
        else:
            # Admin peut marquer toutes les alertes comme vues
            pass
        
        # Marquer comme vue
        alerte.statut = "vue"
        alerte.vue_par = str(current_user.id)
        alerte.date_vue = datetime.utcnow()
        alerte.updated_at = datetime.utcnow()
        
        await alerte.save()
        
        return {"message": "Alerte marquée comme vue"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du marquage: {str(e)}")
