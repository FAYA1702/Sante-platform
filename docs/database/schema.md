# Schéma de la Base de Données

## Collections Principales

### Utilisateurs (`users`)
```javascript
{
  _id: ObjectId,
  username: String,      // unique
  email: String,         // unique
  hashed_password: String,
  role: String,         // 'patient', 'medecin', 'admin', 'technicien'
  is_active: Boolean,
  created_at: DateTime,
  updated_at: DateTime,
  last_login: DateTime
}
```

### Données de Santé (`health_data`)
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,    // Référence à l'utilisateur
  type: String,        // 'heart_rate', 'blood_pressure', 'oxygen_level', etc.
  value: Number,
  unit: String,        // 'bpm', 'mmHg', '%', etc.
  timestamp: DateTime,
  device_id: String,   // ID du dispositif source
  is_anomaly: Boolean, // Drapeau d'anomalie détectée par l'IA
  metadata: Object     // Données supplémentaires
}
```

### Recommandations (`recommendations`)
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,    // Référence à l'utilisateur
  title: String,       // Titre de la recommandation
  description: String,  // Description détaillée
  type: String,        // 'warning', 'info', 'critical'
  source: String,      // 'ia', 'medecin', 'system'
  is_read: Boolean,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Alertes (`alerts`)
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,    // Référence à l'utilisateur
  message: String,
  severity: String,    // 'low', 'medium', 'high', 'critical'
  type: String,        // 'anomaly', 'device_offline', 'threshold_exceeded'
  is_resolved: Boolean,
  resolved_at: DateTime,
  created_at: DateTime
}
```

## Index

```javascript
// Collection users
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ email: 1 }, { unique: true });

// Collection health_data
db.health_data.createIndex({ user_id: 1, timestamp: -1 });
db.health_data.createIndex({ type: 1, timestamp: -1 });

// Collection recommendations
db.recommendations.createIndex({ user_id: 1, created_at: -1 });

// Collection alerts
db.alerts.createIndex({ user_id: 1, created_at: -1 });
db.alerts.createIndex({ is_resolved: 1, severity: -1 });
```

## Relations

1. Un utilisateur (`users`) peut avoir plusieurs entrées de données de santé (`health_data`)
2. Un utilisateur peut avoir plusieurs recommandations (`recommendations`)
3. Un utilisateur peut avoir plusieurs alertes (`alerts`)
4. Les données de santé peuvent déclencher des recommandations et des alertes
