# Système d'Assignation Patient-Médecin

## Vue d'ensemble

Le système d'assignation respecte strictement le cahier des charges en implémentant un contrôle d'accès basé sur les rôles (RBAC) où seuls les **techniciens médicaux** peuvent gérer les assignations patient-médecin.

## Architecture

### Rôles et Permissions

- **Technicien médical** : Seul rôle autorisé à gérer les assignations
- **Patient** : Aucun choix de médecin lors de l'inscription
- **Médecin** : Voit uniquement ses patients assignés (ségrégation des données)
- **Admin** : Gestion des utilisateurs, pas d'accès aux assignations médicales

### Endpoints Backend

#### `/assignations` (Techniciens uniquement)

- `GET /assignations/patients-sans-assignation` - Liste des patients sans médecin
- `GET /assignations/medecins-disponibles` - Médecins avec charge de travail
- `POST /assignations/assigner` - Assignation manuelle
- `POST /assignations/assigner-ia` - Assignation assistée par IA
- `GET /assignations/historique` - Historique des assignations
- `DELETE /assignations/{patient_id}` - Désassignation

## Interface Technicien

### Page `/assignations`

L'interface est organisée en 3 onglets :

1. **Patients sans assignation**
   - Liste des patients nécessitant une assignation
   - Informations : nom, département, spécialité requise
   - Boutons d'action : assignation manuelle ou IA

2. **Médecins disponibles**
   - Liste des médecins avec leur charge de travail
   - Informations : nom, département, spécialité, nombre de patients
   - Indicateur de disponibilité (charge < 10 patients)

3. **Historique des assignations**
   - Journal des assignations effectuées
   - Type : manuelle ou IA
   - Statut : active, terminée
   - Date et technicien responsable

## Algorithme IA d'Assignation

### Service `IAAssignationService`

L'IA suggère le médecin optimal basé sur :

1. **Correspondance spécialité** (50 points)
   - Vérification département/spécialité requise
   
2. **Charge de travail** (30 points max)
   - Moins de patients = score plus élevé
   - Formule : `max(0, 30 - (charge_travail * 3))`

3. **Facteur aléatoire** (20 points max)
   - Évite la prédictibilité totale

### Processus d'Assignation IA

1. Technicien clique "Assignation IA"
2. Backend appelle le service IA
3. IA analyse les critères et calcule les scores
4. Suggestion du médecin optimal
5. Technicien valide ou modifie l'assignation

## Sécurité et Conformité

### RBAC (Role-Based Access Control)

- Middleware `verifier_roles` sur tous les endpoints
- Vérification du rôle `technicien` obligatoire
- Rejet automatique pour autres rôles

### Ségrégation des Données

- Un patient = un médecin référent maximum
- Médecins voient uniquement leurs patients
- Pas d'accès croisé entre départements

### Conformité RGPD/HIPAA

- Chiffrement AES-256 des données sensibles
- Anonymisation des logs
- Audit trail des assignations
- Consentement patient implicite

## Données de Test

### Comptes Utilisateurs

```
Technicien : technicien@example.com / password
Patient    : testP1@gmail.com (sans assignation)
Médecin 1  : Doc1@gmail.com (Cardiologie)
Médecin 2  : Doc2@gmail.com (Pneumologie)
Admin      : admin@example.com
```

### Départements

- **Cardiologie** : spécialités cardiologie, chirurgie cardiaque
- **Pneumologie** : spécialités pneumologie, allergologie

## Workflow d'Assignation

1. **Inscription Patient**
   - Aucune assignation automatique
   - Patient ajouté à la liste "sans assignation"

2. **Assignation par Technicien**
   - Connexion avec compte technicien
   - Accès à `/assignations`
   - Sélection patient + médecin (manuel ou IA)
   - Validation et enregistrement

3. **Suivi Post-Assignation**
   - Patient voit son médecin référent
   - Médecin voit le nouveau patient
   - Historique mis à jour

## Maintenance

### Monitoring

- Logs des assignations dans la collection `assignations`
- Métriques de charge de travail des médecins
- Alertes en cas de surcharge (>10 patients/médecin)

### Évolutions Futures

- Algorithme IA plus sophistiqué (ML)
- Assignations temporaires/urgences
- Réassignation automatique en cas d'absence
- Intégration calendrier médecin

## Dépannage

### Erreurs Communes

1. **403 Forbidden** : Utilisateur non-technicien
2. **404 Patient introuvable** : Patient déjà assigné
3. **500 IA Service** : Service IA indisponible

### Vérifications

```bash
# Vérifier les rôles utilisateurs
db.utilisateurs.find({}, {email: 1, role: 1})

# Patients sans assignation
db.utilisateurs.find({role: "patient", medecin_assigne: null})

# Charge de travail médecins
db.utilisateurs.aggregate([
  {$match: {role: "medecin"}},
  {$lookup: {from: "utilisateurs", localField: "_id", foreignField: "medecin_assigne", as: "patients"}},
  {$project: {email: 1, charge: {$size: "$patients"}}}
])
```
