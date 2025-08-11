"""Script d'initialisation de la base MongoDB pour le projet Santé Platform.

Ce script :
1. Se connecte à MongoDB (localhost:27017).
2. Initialise Beanie avec la base `sante`.
3. Crée des exemples d'utilisateurs, appareils, données de santé, alertes et recommandations.

Exécution :
    python -m backend.scripts.init_db

Assurez-vous que MongoDB est démarré localement avant d'exécuter le script.
"""

import asyncio
from datetime import datetime

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from backend.models.utilisateur import Utilisateur, Role
from backend.models.device import Device
from backend.models.donnee import Donnee
from backend.models.alerte import Alerte
from backend.models.recommandation import Recommandation
from backend.utils.auth import hacher_mot_de_passe


import os

# URI MongoDB par défaut : on lit la variable d'environnement MONGO_URI.
# - En conteneur Docker, MONGO_URI=mongodb://mongo:27017
# - En local, laissez vide pour utiliser localhost.
MONGODB_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
import os
DB_NAME = os.getenv("MONGO_DB_NAME", "sante_db")


async def main() -> None:
    """Initialise la base et insère des données de démonstration."""
    client = AsyncIOMotorClient(MONGODB_URI)
    await init_beanie(database=client[DB_NAME], document_models=[
        Utilisateur,
        Device,
        Donnee,
        Alerte,
        Recommandation,
    ])

    # Nettoyage éventuel pour éviter les doublons lors de ré-exécutions
    await Utilisateur.delete_all()
    await Device.delete_all()
    await Donnee.delete_all()
    await Alerte.delete_all()
    await Recommandation.delete_all()

    # --- Création d'utilisateurs ---
    patient = await Utilisateur(
        email="patient@example.com",
        username="patient",
        mot_de_passe_hache=hacher_mot_de_passe("patient123"),
        role=Role.patient,
    ).insert()

    medecin = await Utilisateur(
        email="medecin@example.com",
        username="drsmith",
        mot_de_passe_hache=hacher_mot_de_passe("doctor123"),
        role=Role.medecin,
    ).insert()

    admin = await Utilisateur(
        email="admin@example.com",
        username="admin",
        mot_de_passe_hache=hacher_mot_de_passe("admin123"),
        role=Role.admin,
    ).insert()

    # --- Appareil ---
    oxymetre = await Device(
        type="oxymètre",
        numero_serie="OX123456",
        user_id=str(patient.id),
    ).insert()

    # --- Donnée de santé ---
    await Donnee(
        device_id=str(oxymetre.id),
        user_id=str(patient.id),
        frequence_cardiaque=75,
        pression_arterielle="118/79",
        taux_oxygene=98,
        date=datetime.utcnow(),
    ).insert()

    # --- Alerte ---
    await Alerte(
        message="Tension légèrement élevée",
        niveau="moyen",
    ).insert()

    # --- Recommandations ---
    await Recommandation(
        user_id=str(patient.id),
        titre="Hydratation",
        description="Buvez au moins 1,5L d'eau par jour pour maintenir une bonne hydratation. Évitez les boissons sucrées.",
        date=datetime.utcnow(),
    ).insert()

    await Recommandation(
        user_id=str(patient.id),
        titre="Activité physique",
        description="Marchez 30 minutes par jour pour améliorer votre circulation sanguine et votre santé cardiovasculaire.",
        date=datetime.utcnow(),
    ).insert()

    await Recommandation(
        user_id=str(patient.id),
        titre="Surveillance de la tension",
        description="Votre tension artérielle est légèrement élevée. Évitez le sel et consultez votre médecin si cela persiste.",
        date=datetime.utcnow(),
    ).insert()

    print("\u2705 Base MongoDB initialisée avec succès !")


if __name__ == "__main__":
    asyncio.run(main())
