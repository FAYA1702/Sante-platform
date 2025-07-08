# Spécifications API - Plateforme de Surveillance de Santé Assistée par IA

## Authentification
### POST /auth/signup
Request:
```json
{
  "email": "user@example.com",
  "mot_de_passe": "string"
}
```
Response 201:
```json
{ "id": "uuid", "email": "user@example.com" }
```

### POST /auth/login
Request:
```json
{
  "email": "user@example.com",
  "mot_de_passe": "string"
}
```
Response 200:
```json
{ "access_token": "jwt-token", "token_type": "bearer" }
```

## Utilisateur
### GET /user/profile
Headers: Authorization: Bearer <token>
Response 200:
```json
{
  "id": "uuid",
  "nom": "string",
  "email": "string",
  "role": "string"
}
```

### PUT /user/profile
Headers: Authorization: Bearer <token>
Request:
```json
{
  "nom": "string",
  "mot_de_passe": "string"
}
```
Response 200: mise à jour réussie

## Appareils Connectés
### GET /devices
Headers: Authorization: Bearer <token>
Response 200:
```json
[ { "id": "uuid", "type": "string", "numero_serie": "string" } ]
```

### POST /devices
Headers: Authorization: Bearer <token>
Request:
```json
{ "type": "string", "numero_serie": "string" }
```
Response 201:
```json
{ "id": "uuid", "type": "string", "numero_serie": "string" }
```

## Données Santé
### POST /data
Headers: Authorization: Bearer <token>
Request:
```json
{
  "device_id": "uuid",
  "frequence_cardiaque": 72.5,
  "pression_arterielle": "120/80",
  "taux_oxygene": 98.0,
  "date": "2025-07-07T10:00:00Z"
}
```
Response 201: données stockées

### GET /data
Headers: Authorization: Bearer <token>
Query params: `?from=ISODate&to=ISODate`
Response 200:
```json
[ { "id": "uuid", "device_id": "uuid", "frequence_cardiaque": 72.5, ... } ]
```

## Alertes
### GET /alerts
Headers: Authorization: Bearer <token>
Response 200:
```json
[ { "id": "uuid", "message": "string", "niveau": "string", "date": "ISODate" } ]
```

## Recommandations
### GET /recommendations
Headers: Authorization: Bearer <token>
Response 200:
```json
[ { "id": "uuid", "contenu": "string", "date": "ISODate" } ]
```
