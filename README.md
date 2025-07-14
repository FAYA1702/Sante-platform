# Santé Platform

## Présentation

Plateforme web de suivi santé connectée (IoT médical, alertes IA, dashboard, gestion utilisateurs) développée en fullstack :
- **Frontend** : React.js (Vite, TypeScript, Tailwind CSS)
- **Backend** : FastAPI (Python), MongoDB (Beanie ODM)
- **Conteneurisation** : Docker, docker-compose
- **Cloud cible** : Azure (prévu)

---

## Architecture & flux principal

```mermaid
graph TD;
  Utilisateur-->|Web|Frontend[Frontend React]
  Frontend-->|API REST (JWT)|Backend[Backend FastAPI]
  Backend-->|ODM|MongoDB[(MongoDB)]
  Backend-->|Notifications|Microservice[Microservice IA/Notifications]
```

- **Authentification** : JWT, gestion des rôles (patient, admin, technicien, médecin)
- **Dashboard** : cartes statistiques, alertes récentes, graphiques santé (Chart.js)
- **Sécurité** : mot de passe haché (bcrypt), endpoints protégés, RBAC
- **Extensible** : IA, RGPD, CI/CD, Azure (voir plan)

---

## Démarrage rapide

```bash
docker compose up --build
```
- Accès : http://localhost:5173 (frontend), http://localhost:8000/docs (API Swagger)

---

## Notes pédagogiques
- **Code abondamment commenté en français** : chaque module explique son rôle, les flux, et les choix techniques.
- **Lisibilité** : structure claire, séparation frontend/backend, schémas et docstrings.
- **Prêt pour présentation orale ou soutenance**.

---

## Pour aller plus loin
- Ajouter le microservice IA/notifications (voir `/backend/routers/alertes.py`)
- Déployer sur Azure (Kubernetes, CosmosDB)
- Finaliser la documentation RGPD et sécurité

---

*Pour toute question, voir les commentaires dans le code ou demander à l’auteur.*
