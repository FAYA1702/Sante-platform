# Architecture du Système

## 1. Diagramme d'Architecture Global

```mermaid
flowchart TD
    subgraph Client
        A[Application Web] -->|HTTPS| B[API Gateway]
        C[Application Mobile] -->|HTTPS| B
    end

    subgraph Cloud[Cloud Azure]
        B -->|Load Balancing| D[Service Backend]
        D --> E[(MongoDB)]
        D --> F[(Redis)]
        D --> G[Service IA]
        G --> E
        G --> F
        G --> H[Azure Functions]
        H --> I[Azure Storage]
    end

    subgraph IoT[Dispositifs IoT]
        J[Capteurs] -->|MQTT/HTTPS| K[IoT Hub]
        K --> B
    end

    subgraph Monitoring[Monitoring]
        L[Prometheus] --> M[Grafana]
        N[Application Insights]
    end

    D --> L
    G --> L
    K --> L
```

## 2. Diagramme de Déploiement

```mermaid
graph TD
    subgraph Azure[Cloud Azure]
        A[Azure App Service] -->|Conteneur| B[Backend]
        A -->|Conteneur| C[Frontend]
        D[Azure Container Instances] -->|Conteneur| E[Service IA]
        F[Azure Cache for Redis]
        G[Azure Cosmos DB (MongoDB API)]
        H[Azure Storage]
        I[Azure Monitor]
        
        B <--> F
        B <--> G
        E <--> F
        E <--> G
        E <--> H
        
        I -->|Surveillance| A
        I -->|Surveillance| D
        I -->|Surveillance| F
        I -->|Surveillance| G
    end
    
    Client[Client Web/Mobile] -->|HTTPS| A
    IoT[Dispositifs IoT] -->|MQTT/HTTPS| A
```

## 3. Flux de Données

```mermaid
sequenceDiagram
    participant C as Client
    participant F as Frontend
    participant B as Backend
    participant DB as MongoDB
    participant R as Redis
    participant I as Service IA
    
    C->>F: Connexion utilisateur
    F->>B: POST /auth/login
    B->>DB: Vérification identifiants
    B-->>F: JWT Token
    
    loop Surveillance Continue
        C->>F: Envoi données capteurs
        F->>B: POST /data (avec JWT)
        B->>DB: Stockage données
        B->>R: Publication événement
        R->>I: Notification nouvelle donnée
        I->>DB: Analyse des données
        alt Anomalie détectée
            I->>DB: Création alerte
            I->>R: Notification alerte
            R->>F: Mise à jour en temps réel (SSE)
        end
    end
```

## 4. Architecture de Sécurité

```mermaid
graph LR
    A[Client] -->|1. Auth JWT| B[API Gateway]
    B -->|2. Validation JWT| C[Backend Services]
    C -->|3. RBAC| D[(Base de données)]
    
    E[Dispositifs IoT] -->|4. Certificats X.509| F[IoT Hub]
    F -->|5. Données chiffrées| C
    
    G[Admin] -->|6. MFA| H[Portail Admin]
    H -->|7. RBAC strict| I[Services Admin]
    
    style A fill:#f9f,stroke:#333
    style E fill:#9cf,stroke:#333
    style G fill:#9f9,stroke:#333
```

## 5. Flux de Données de Santé

```mermaid
flowchart LR
    A[Capteurs] -->|1. Données brutes| B[Collecte]
    B -->|2. Validation| C[Transformation]
    C -->|3. Données structurées| D[Stockage]
    D -->|4. Notification| E[Analyse IA]
    E -->|5. Résultats| F[Tableau de bord]
    E -->|6. Alertes| G[Notifications]
    
    subgraph Traitement
        B --> H[Validation]
        C --> I[Nettoyage]
        D --> J[Base de données]
    end
    
    subgraph Analyse
        E --> K[Modèles ML]
        E --> L[Règles métier]
    end
```

## Légende
- **Lignes pleines** : Flux de données principal
- **Lignes pointillées** : Flux secondaire ou événementiel
- **Rectangles arrondis** : Composants système
- **Parallélogrammes** : Données ou événements
