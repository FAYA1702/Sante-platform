from fastapi import FastAPI
from beanie import init_beanie
from models import Device, Donnee, Alerte, Recommandation
from db import get_client
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, appareils, donnees, alertes, recommandations

app = FastAPI(title="Sante Platform API", version="0.1.0")


@app.on_event("startup")
async def on_startup():
    """Initialise Beanie avec la connexion Mongo."""
    client = get_client()
    await init_beanie(database=client['sante_db'], document_models=[Device, Donnee, Alerte, Recommandation])

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


@app.get("/ping")
async def ping():
    return {"status": "ok"}
