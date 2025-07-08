from fastapi import FastAPI
from beanie import init_beanie
from backend.models import Device, Donnee, Alerte, Recommandation, Utilisateur
from backend.db import get_client
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import auth, appareils, donnees, alertes, recommandations, protected

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialisation Beanie lors du démarrage, remplacement de on_event."""
    client = get_client()
    await init_beanie(database=client["sante_db"], document_models=[Device, Donnee, Alerte, Recommandation, Utilisateur])
    yield
    # Pas d'opérations de shutdown spécifiques pour l'instant


app = FastAPI(title="Sante Platform API", version="0.1.0", lifespan=lifespan)




# CORS (allow React dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(appareils.router, tags=["appareils"])
app.include_router(donnees.router, tags=["donnees"])
app.include_router(alertes.router, tags=["alertes"])
app.include_router(recommandations.router, tags=["recommandations"])
app.include_router(protected.router)


@app.get("/ping")
async def ping():
    return {"status": "ok"}
