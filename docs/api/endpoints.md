# Documentation de l'API

## Authentification

### `POST /auth/login`
Authentifie un utilisateur et retourne un token JWT.

**Paramètres :**
```json
{
  "username": "string",
  "password": "string"
}
```

**Réponse :**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

## Utilisateurs

### `GET /users/me`
Récupère les informations de l'utilisateur connecté.

**En-têtes requis :**
- `Authorization: Bearer <token>`

**Réponse :**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "role": "patient|medecin|admin|technicien",
  "is_active": true
}
```

## Données de Santé

### `GET /data`
Récupère les données de santé de l'utilisateur connecté.

**Paramètres de requête :**
- `start_date`: Date de début (optionnel)
- `end_date`: Date de fin (optionnel)
- `type`: Type de données (ex: 'heart_rate', 'blood_pressure') (optionnel)

**En-têtes requis :**
- `Authorization: Bearer <token>`

## Recommandations

### `GET /recommendations`
Récupère les recommandations générées par l'IA pour l'utilisateur connecté.

**En-têtes requis :**
- `Authorization: Bearer <token>`

## Alertes

### `GET /alerts`
Récupère les alertes générées par le système.

**En-têtes requis :**
- `Authorization: Bearer <token>`

### `GET /alerts/stream`
Flux SSE (Server-Sent Events) pour recevoir les alertes en temps réel.

**En-têtes requis :**
- `Authorization: Bearer <token>`
