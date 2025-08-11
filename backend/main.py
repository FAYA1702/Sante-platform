from fastapi import FastAPI
from beanie import init_beanie
from backend.models import Device, Donnee, Alerte, Utilisateur, Department, Referral, Assignment
from backend.models.recommandation import Recommandation
from backend.db import get_client, MONGO_DB_NAME
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import (
    auth, appareils, donnees, alertes, recommandations, stats, users, patients, medecin,
    filtrage_medical, assignation, departments, referrals, assignments, protected, admin
)

from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialisation Beanie lors du démarrage, remplacement de on_event."""
    client = get_client()
    await init_beanie(database=client[MONGO_DB_NAME], document_models=[Device, Donnee, Alerte, Recommandation, Utilisateur, Department, Referral, Assignment])
    yield
    # Pas d'opérations de shutdown spécifiques pour l'instant


app = FastAPI(title="Sante Platform API", version="0.1.0", lifespan=lifespan)




# CORS (allow React dev server)
# Liste blanche des origines autorisées (frontend)
origins = [
    "http://localhost:5173",  # Frontend Vite (développement)
    "http://localhost:5174",  # Frontend Vite (port alternatif)
    "http://localhost:5175",  # Frontend Vite (port alternatif 2)
    "http://localhost:3000",  # Autre port React éventuel
]

# -----------------------------------------------------------------------------
# Configuration CORS
# -----------------------------------------------------------------------------
# Selon la spécification CORS, l’en-tête Authorization est considéré comme un
# « credential ».  Pour permettre l’envoi du JWT depuis le frontend, il faut :
#   1. activer allow_credentials=True (ce qui ajoute Access-Control-Allow-Credentials)
#   2. ne pas utiliser l’astérisque * pour allow_origins
#
# En mode développement, on autorise toutes les origines localhost quel que soit le port.
# En production, restreindre la liste aux domaines frontaux officiels.
# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Utilise la liste des origines définie plus haut
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=600,  # Durée de mise en cache des pré-vérifications CORS en secondes
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(appareils.router, tags=["appareils"])
app.include_router(donnees.router, tags=["donnees"])
app.include_router(alertes.router, tags=["alertes"])
app.include_router(recommandations.router)
app.include_router(stats.router)
app.include_router(users.router)
app.include_router(patients.router)
app.include_router(medecin.router)
app.include_router(filtrage_medical.router)
app.include_router(assignation.router)
app.include_router(departments.router)
app.include_router(referrals.router)
app.include_router(assignments.router)
app.include_router(protected.router)
app.include_router(admin.router, prefix="/admin", tags=["admin"])

from fastapi.openapi.utils import get_openapi


def custom_openapi():
    """Génère un schéma OpenAPI incluant la sécurité JWT afin que Swagger
    affiche le bouton Authorize (cadenas)."""
    openapi_schema = app.openapi_schema if app.openapi_schema else get_openapi(
        title=app.title,
        version=app.version,
        description="API de la plateforme santé",
        routes=app.routes,
    )

    # Déclare le schéma de sécurité HTTPBearer s'il n'existe pas déjà
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})["HTTPBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    # Référence globale au schéma pour que Swagger affiche le bouton Authorize
    if {"HTTPBearer": []} not in openapi_schema.setdefault("security", []):
        openapi_schema["security"].append({"HTTPBearer": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.get("/test-cors")
async def test_cors():
    """Endpoint de test pour vérifier que CORS fonctionne (sans auth)."""
    return {"message": "CORS fonctionne !", "timestamp": "2025-07-18"}
