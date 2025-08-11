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
from bson import ObjectId

import motor.motor_asyncio
import redis.asyncio as redis  # type: ignore
from fastapi import FastAPI
from pydantic import BaseModel, Field
from beanie import init_beanie
from models import Recommandation

LOGGER = logging.getLogger("ia_service")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sante_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

ALERT_CHANNEL = "notify"
SOURCE_CHANNEL = "nouvelle_donnee"

# Seuils paramétrables via variables d’environnement
FC_MAX = int(os.getenv("FC_MAX", "100"))  # Tachycardie au-delà de X bpm
SPO2_MIN = int(os.getenv("SPO2_MIN", "92"))  # Hypoxie en-dessous de X %


class Alerte(BaseModel):
    user_id: str = Field(...)
    message: str = Field(...)
    niveau: str = Field(..., pattern="^(normal|warning|critical)$")
    date: str = Field(...)
    # Nouveaux champs pour le filtrage médical
    priorite_medicale: str = Field(default="normale")
    visible_patient: bool = Field(default=True)
    # Champ pour la proposition de département
    suggested_department_code: str = Field(default="GENERAL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise les clients Redis + Mongo et lance la tâche worker."""
    mongo_client = None
    redis_client = None
    task = None
    
    try:
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
        db = mongo_client[MONGO_DB_NAME]
        # Initialiser Beanie pour la collection recommandations
        await init_beanie(database=db, document_models=[Recommandation])

        async def worker():
            LOGGER.info("Démarrage du worker Redis IA...")
            backoff = 1
            while True:
                try:
                    LOGGER.info("Tentative de connexion Redis...")
                    pubsub = redis_client.pubsub()
                    await pubsub.subscribe(SOURCE_CHANNEL)
                    LOGGER.info("IA Service : abonné à %s", SOURCE_CHANNEL)
                    
                    async for message in pubsub.listen():
                        if message["type"] != "message":
                            continue
                        try:
                            LOGGER.info("Message Redis reçu : %s", message["data"])
                            payload: Dict[str, Any] = json.loads(message["data"])
                            await analyser_donnee(payload, db, redis_client)
                        except Exception as exc:  # pragma: no cover
                            LOGGER.exception("Erreur traitement IA: %s", exc)
                    # Si la boucle se termine sans exception, reset backoff
                    backoff = 1
                except Exception as exc:
                    LOGGER.error("Connexion Redis perdue (%s). Reconnexion dans %s s", exc, backoff)
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 60)  # cap 60s

        LOGGER.info("Création de la tâche worker Redis...")
        task = asyncio.create_task(worker())
        LOGGER.info("Worker Redis créé, démarrage de l'application...")
        yield
        
    finally:
        # Cleanup propre
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        if mongo_client:
            mongo_client.close()
        if redis_client:
            await redis_client.aclose()


aapp = FastAPI(title="IA Service", lifespan=lifespan)  # noqa: N818 (alias évite conflit)


@aapp.get("/health", tags=["système"])
async def health():  # noqa: D401
    """Endpoint de liveness probe."""
    return {"status": "ok"}


def proposer_departement(alerte_message: str, fc: float = None, spo2: float = None) -> str:
    """Propose un département médical basé sur l'analyse IA des symptômes."""
    
    # Logique de proposition basée sur les symptômes détectés
    if "Tachycardie" in alerte_message or (fc and fc > 120):
        # Problèmes cardiaques → Cardiologie
        return "CARDIO"
    elif "Hypoxie" in alerte_message or (spo2 and spo2 < 85):
        # Problèmes respiratoires sévères → Médecine Générale (urgence)
        return "GENERAL"
    elif spo2 and spo2 < 92:
        # Problèmes respiratoires modérés → Médecine Générale
        return "GENERAL"
    elif fc and 90 <= fc <= 120:
        # Surveillance cardiaque → Cardiologie
        return "CARDIO"
    else:
        # Par défaut → Médecine Générale
        return "GENERAL"


async def creer_referral_automatique(user_id: str, suggested_department_code: str, alerte_message: str, db: Any) -> None:
    """Crée automatiquement une orientation (referral) vers le département suggéré par l'IA."""
    
    try:
        # Récupérer l'ID du département suggéré
        department = await db["departments"].find_one({"code": suggested_department_code, "is_active": True})
        if not department:
            LOGGER.warning(f"Département {suggested_department_code} non trouvé, utilisation de GENERAL")
            department = await db["departments"].find_one({"code": "GENERAL", "is_active": True})
            if not department:
                LOGGER.error("Aucun département par défaut trouvé")
                return
        
        # Vérifier si le patient a déjà une orientation pending vers ce département
        existing_referral = await db["referrals"].find_one({
            "patient_id": user_id,
            "proposed_department_id": str(department["_id"]),
            "status": "pending"
        })
        
        if existing_referral:
            LOGGER.info(f"Orientation existante pour patient {user_id} vers {suggested_department_code}")
            return
        
        # Créer une nouvelle orientation
        from datetime import datetime
        referral_data = {
            "patient_id": user_id,
            "proposed_department_id": str(department["_id"]),
            "status": "pending",
            "source": "IA",
            "notes": f"Orientation automatique générée par l'IA suite à : {alerte_message}",
            "created_by": None,  # Créé par l'IA
            "processed_by": None,
            "processed_at": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db["referrals"].insert_one(referral_data)
        LOGGER.info(f"Orientation IA créée : patient {user_id} → département {suggested_department_code}")
        
    except Exception as e:
        LOGGER.error(f"Erreur lors de la création de l'orientation automatique : {e}")


async def analyser_donnee(payload: Dict[str, Any], db: Any, redis_client: Any) -> None:  # type: ignore
    """Analyse la nouvelle donnée puis crée une alerte si nécessaire."""
    donnee_id = payload.get("donnee_id")
    if not donnee_id:
        return

    # Utilise ObjectId pour requêter correctement le document
    try:
        oid = ObjectId(donnee_id)
    except Exception:
        LOGGER.warning("ID Mongo invalide reçu: %s", donnee_id)
        return

    donnee = await db["donnees"].find_one({"_id": oid})
    if not donnee:
        return

    alerts: list[Alerte] = []
    fc = donnee.get("frequence_cardiaque")
    spo2 = donnee.get("taux_oxygene")

    if fc is not None and fc > FC_MAX:
        # Tachycardie : priorité élevée, visible patient
        suggested_dept = proposer_departement("Tachycardie détectée", fc=fc, spo2=spo2)
        alerts.append(
            Alerte(
                user_id=str(donnee["user_id"]),
                message="Tachycardie détectée",
                niveau="warning",
                date=donnee["date"].isoformat() if hasattr(donnee["date"], 'isoformat') else str(donnee["date"]),
                priorite_medicale="elevee",
                visible_patient=True,  # Patient peut voir cette alerte
                suggested_department_code=suggested_dept
            )
        )
    if spo2 is not None and spo2 < SPO2_MIN:
        # Hypoxie : priorité critique, visible patient avec précaution
        suggested_dept = proposer_departement("Hypoxie détectée", fc=fc, spo2=spo2)
        alerts.append(
            Alerte(
                user_id=str(donnee["user_id"]),
                message="Hypoxie détectée",
                niveau="critical",
                date=donnee["date"].isoformat() if hasattr(donnee["date"], 'isoformat') else str(donnee["date"]),
                priorite_medicale="critique",
                visible_patient=False,  # Masqué au patient pour éviter la panique
                suggested_department_code=suggested_dept
            )
        )

    for alerte in alerts:
        await db["alertes"].insert_one(alerte.model_dump())
        await redis_client.publish(ALERT_CHANNEL, alerte.model_dump_json())
        LOGGER.info("Alerte générée et publiée : %s (département suggéré: %s)", alerte.message, alerte.suggested_department_code)
        
        # Créer automatiquement une orientation vers le département suggéré
        await creer_referral_automatique(
            user_id=alerte.user_id,
            suggested_department_code=alerte.suggested_department_code,
            alerte_message=alerte.message,
            db=db
        )

        # Génération automatique d'une recommandation médicale (Beanie)
        titre = None
        description = None
        priorite = "normale"
        visible_patient = True
        validation_medicale = False
        
        if alerte.message == "Tachycardie détectée":
            titre = "⚠️ Surveillance cardiaque recommandée"
            description = f"Tachycardie détectée avec une fréquence cardiaque supérieure à {FC_MAX} bpm. Il est recommandé de consulter un professionnel de santé pour évaluation et surveillance."
            priorite = "elevee"
            visible_patient = True  # Patient peut voir cette recommandation
            validation_medicale = False  # Nécessite validation médecin
        elif alerte.message == "Hypoxie détectée":
            titre = "🚑 Surveillance respiratoire urgente"
            description = f"Hypoxie détectée avec un taux d'oxygène inférieur à {SPO2_MIN}%. Consultation médicale urgente recommandée pour évaluer la fonction respiratoire."
            priorite = "critique"
            visible_patient = False  # Masqué au patient, médecin doit valider
            validation_medicale = False  # Nécessite validation médecin
        
        # Désactivé : la génération automatique de recommandations médicales par l'IA est désactivée pour garantir la validation humaine.
        # if titre and description:
        #     from datetime import datetime
        #     date_obj = datetime.fromisoformat(alerte.date.replace('Z', '+00:00')) if isinstance(alerte.date, str) else alerte.date
        #     recommandation = Recommandation(
        #         user_id=alerte.user_id,
        #         titre=titre,
        #         description=description,
        #         date=date_obj,
        #         statut="nouvelle",  # Statut par défaut pour les nouvelles recommandations
        #         priorite_medicale=priorite,
        #         visible_patient=visible_patient,
        #         validation_medicale=validation_medicale,
        #         created_at=date_obj,
        #         updated_at=date_obj,
        #         is_active=True
        #     )
        #     await recommandation.insert()
        #     LOGGER.info("Recommandation IA générée pour user %s : %s (priorité: %s, visible patient: %s)", 
        #                alerte.user_id, titre, priorite, visible_patient)
        # Les recommandations seront désormais créées et validées exclusivement par un médecin via l'interface dédiée.
