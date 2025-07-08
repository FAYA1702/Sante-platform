# CI/CD, Monitoring et Tests - Plateforme Santé IA

## 1. CI/CD (GitHub Actions / GitLab CI)

### Workflows
- **CI** (sur push et PR) :
  1. Checkout code
  2. Installer dépendances (frontend & backend)
  3. Linting (ESLint, flake8)
  4. Tests unitaires (pytest, jest)
  5. Build frontend (npm run build)
- **CD** (sur merge vers main) :
  1. Déploiement staging (Azure Dev/Test)
  2. Tests d’intégration automatiques
  3. Promotion en production (tag/v1.x.x)

### Branching
- **main** : code validé en production
- **develop** : intégration continue, staging
- **feature/***, **hotfix/***

## 2. Monitoring et Alerting

- **Logs** : JSON structuré, centralisé sur Azure Monitor ou ELK Stack
- **Métriques** : Prometheus + Grafana ou Azure Metrics :
  - Latence des API
  - Taux d’erreur (5xx)
  - RPS (requêtes/sec)
- **Alerting** : seuils (latence > 200ms, erreurs > 1% sur 5mn)
  - Notifications Slack/email/SMS via Notification Service

## 3. Tests

- **Unitaires** : pytest (backend), jest/react-testing-library (frontend)
- **Intégration** : Postman/Newman ou pytest + testcontainers
- **End-to-End** : Cypress (scénarios clés : inscription, connexion, envoi données)
- **Performance/Charge** : Locust ou k6 (1000 utilisateurs virtuels)

## 4. Qualité de code

- Coverage minimum : 80%
- Pull Request : 2 reviewers minimum
- Security : Dependabot, Snyk (vuln. critiques bloquantes)
