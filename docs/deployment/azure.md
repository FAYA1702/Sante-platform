# Déploiement Azure - Container Apps + ACR

Ce guide décrit le déploiement de la plateforme vers Azure Container Apps avec Azure Container Registry (ACR) via GitHub Actions (`.github/workflows/azure-deploy.yml`).

## Prérequis
- Abonnement Azure avec droits Contributeur
- Azure CLI ≥ 2.57 (`az version`)
- GitHub repository (où vit ce code)
- Images Docker construites par le workflow (gérées automatiquement)

## Ressources à créer (one-time)
Variables à définir (adaptez):
```
RG=sante-rg
LOCATION=canadaeast   # ou westeurope, francecentral, etc.
ACR_NAME=santesdkacr   # unique global (lettres/chiffres)
ENV_NAME=sante-ca-env  # nom de l'environnement Container Apps
```

Création ressources:
```
az group create -n $RG -l $LOCATION
az acr create -n $ACR_NAME -g $RG --sku Basic
az containerapp env create -n $ENV_NAME -g $RG -l $LOCATION
```

## Authentification GitHub → Azure (OIDC)
Utiliser OpenID Connect (sans secrets) avec GitHub Actions.

1) Créer une application (Service Principal) et des credentials fédérés:
```
SUBS_ID=$(az account show --query id -o tsv)
az ad app create --display-name sante-gha-app
APP_ID=$(az ad app list --display-name sante-gha-app --query [0].appId -o tsv)
az ad sp create --id $APP_ID
SP_OBJECT_ID=$(az ad sp show --id $APP_ID --query id -o tsv)

# Donner le rôle Contributeur sur le RG
az role assignment create \
  --assignee-object-id $SP_OBJECT_ID \
  --assignee-principal-type ServicePrincipal \
  --role Contributor \
  --scope /subscriptions/$SUBS_ID/resourceGroups/$RG

# Ajouter une crédential OIDC GitHub (remplacer ORG/REPO)
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "gha-oidc",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:ORG/REPO:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

2) Définir Secrets GitHub (Settings → Secrets and variables → Actions):
- AZURE_CLIENT_ID = APP_ID (id de l'app ci-dessus)
- AZURE_TENANT_ID = `az account show --query tenantId -o tsv`
- AZURE_SUBSCRIPTION_ID = `az account show --query id -o tsv`
- AZURE_RESOURCE_GROUP = $RG
- AZURE_LOCATION = $LOCATION
- AZURE_CONTAINERAPPS_ENVIRONMENT = $ENV_NAME
- ACR_NAME = $ACR_NAME

Secrets applicatifs:
- MONGO_URI = URL MongoDB (ex: `mongodb+srv://...` ou `mongodb://<host>:27017`)
- MONGO_DB_NAME = sante_db
- REDIS_URL = `redis://<host>:6379` (si Redis managé/Azure Cache)
- FRONTEND_API_URL = URL publique du backend (remplacée après 1er déploiement)

Note: En prod, utilisez Azure Cosmos DB for MongoDB et Azure Cache for Redis. Sinon, fournissez des endpoints managés accessibles depuis Container Apps.

## Workflow GitHub Actions
Le fichier `/.github/workflows/azure-deploy.yml` effectue:
- Login Azure (OIDC)
- Login ACR
- Build et push des images:
  - backend → `sante-backend:${{ github.sha }}`
  - services/ia_service → `sante-ia-service:${{ github.sha }}`
  - services/notification_service → `sante-notification-service:${{ github.sha }}`
  - frontend → `sante-frontend:${{ github.sha }}`
- Création/MAJ des Container Apps:
  - `sante-backend` (ingress externe, port 8000)
  - `sante-ia-service` (ingress interne, port 8001)
  - `sante-notification-service` (ingress interne, port 8002)
  - `sante-frontend` (ingress externe, port 80)

Commandes (extraits):
```
az containerapp up -n sante-backend -g $RG -e $ENV_NAME \
  -i <ACR>.azurecr.io/sante-backend:TAG --ingress external --target-port 8000 \
  --env-vars MONGO_URI=... MONGO_DB_NAME=sante_db REDIS_URL=... DEMO_MODE=true \
  --runtime-config startupCommand="uvicorn","backend.main:app","--host","0.0.0.0","--port","8000"

# IA service (l'instance FastAPI est `aapp` dans services/ia_service/main.py)
az containerapp up -n sante-ia-service -g $RG -e $ENV_NAME \
  -i <ACR>.azurecr.io/sante-ia-service:TAG --ingress internal --target-port 8001 \
  --env-vars MONGO_URI=... MONGO_DB_NAME=sante_db REDIS_URL=... DEMO_MODE=true \
  --runtime-config startupCommand="uvicorn","main:aapp","--host","0.0.0.0","--port","8001"
```

## Points d'intégration & réseaux
- Container Apps n'expose pas un réseau Docker Compose. Utilisez des URLs/connexions managées (Cosmos Mongo, Azure Cache Redis) ou un VNet si nécessaire.
- FRONTEND_API_URL doit pointer vers l'URL publique de `sante-backend` (après déploiement: `az containerapp show -n sante-backend -g $RG --query properties.configuration.ingress.fqdn -o tsv`).

## Déploiement
- Push sur `main` déclenche le workflow. Vous pouvez aussi lancer manuellement (workflow_dispatch) avec `image_tag`.
- Sur la première exécution, récupérez l'URL publique de `sante-backend` et mettez-la dans le secret `FRONTEND_API_URL`, puis relancez le job pour que le frontend communique avec le backend.

## Observabilité
- Logs:
```
az containerapp logs show -n sante-backend -g $RG --follow
```
- Santé:
  - Backend: `GET /ping`
  - IA: `GET /health`
  - Notifications: `GET /health`

## Sécurité
- Placez toutes les variables sensibles en secrets GitHub.
- Activez TLS par défaut (géré par Container Apps ingress).
- Pour les données, envisager CSFLE (Mongo crypté) et Azure Key Vault pour la gestion des secrets.
