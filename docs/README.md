# Documentation de la Plateforme de Surveillance de Santé

Bienvenue dans la documentation technique de la plateforme de surveillance de santé assistée par IA. Cette documentation est conçue pour aider les développeurs, les administrateurs système et les autres parties prenantes à comprendre, utiliser et maintenir le système.

## 📚 Table des Matières

1. [Architecture du Système](./architecture/overview.md)
   - Vue d'ensemble
   - Composants principaux
   - Flux de données
   - Diagrammes d'architecture

2. [Documentation de l'API](./api/endpoints.md)
   - Authentification
   - Points de terminaison
   - Exemples de requêtes
   - Codes de statut

3. [Base de Données](./database/schema.md)
   - Schéma des collections
   - Index et performances
   - Relations entre les entités
   - Scripts de migration

4. [Sécurité](./security/policies.md)
   - Authentification et autorisation
   - Chiffrement des données
   - Conformité RGPD/HIPAA
   - Journalisation et audit

5. [Intelligence Artificielle](./ia/overview.md)
   - Modèles utilisés
   - Flux de traitement des données
   - Entraînement et évaluation
   - API du service IA

## 🚀 Démarrage Rapide

### Prérequis
- Docker et Docker Compose
- Node.js 18+ et Yarn
- Python 3.10+
- MongoDB 6.0+
- Redis 7.0+

### Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-utilisateur/sante-platform.git
   cd sante-platform
   ```

2. **Configurer les variables d'environnement**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   ```

3. **Démarrer les services**
   ```bash
   # Démarrer les services backend
   docker-compose up -d
   
   # Installer les dépendances frontend
   cd frontend
   yarn install
   
   # Démarrer le serveur de développement
   yarn dev
   ```

4. **Accéder à l'application**
   - Frontend : http://localhost:5173
   - Backend API : http://localhost:8000
   - Documentation API : http://localhost:8000/docs

## 📊 Diagrammes

Consultez les [diagrammes d'architecture](./diagrams/architecture/system_architecture.md) pour une compréhension visuelle du système.

## 🤝 Contribution

Veuillez lire notre [guide de contribution](./CONTRIBUTING.md) pour les détails sur notre code de conduite et le processus de soumission des pull requests.

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](../LICENSE) pour plus de détails.

## 📞 Support

Pour toute question ou assistance, veuillez ouvrir une [issue](https://github.com/votre-utilisateur/sante-platform/issues) ou nous contacter à support@example.com.
