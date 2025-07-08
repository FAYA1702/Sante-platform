# Dockerfile pour le service backend FastAPI
FROM python:3.11-slim

# Empêcher l'invite interactive lors de l'installation de dépendances
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Définir le dossier de travail
# Dossier de travail racine
WORKDIR /app

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python
COPY requirements.txt ./requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source dans un sous-dossier backend pour conserver la structure d'import
COPY . /app/backend

# Exposer le port de l'API
EXPOSE 8000

# Commande de lancement (utilisée en production ; en dev, override avec --reload)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
