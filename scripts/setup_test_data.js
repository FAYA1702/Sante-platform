// Script pour configurer des données de test dans MongoDB
// Utilisation: docker exec sante-platform-mongo-1 mongosh sante_db setup_test_data.js

// 1. Créer un technicien médical pour les tests d'assignation
const technicienId = new ObjectId();
db.utilisateurs.insertOne({
  _id: technicienId,
  email: 'technicien@example.com',
  role: 'technicien',
  nom: 'Technicien',
  prenom: 'Medical',
  mot_de_passe_hash: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5/Qe2', // password: password
  statut: 'actif',
  date_creation: new Date()
});

// 2. Créer des départements si ils n'existent pas
const cardioId = new ObjectId();
const pneumoId = new ObjectId();

try {
  db.departments.insertMany([
    {
      _id: cardioId,
      nom: 'Cardiologie',
      description: 'Département de cardiologie',
      specialites: ['cardiologie', 'chirurgie cardiaque']
    },
    {
      _id: pneumoId,
      nom: 'Pneumologie', 
      description: 'Département de pneumologie',
      specialites: ['pneumologie', 'allergologie']
    }
  ]);
} catch(e) {
  print('Départements déjà existants');
}

// 3. Assigner les médecins aux départements
db.utilisateurs.updateOne(
  {email: 'Doc1@gmail.com'},
  {$set: {
    department_id: cardioId,
    specialite: 'cardiologie',
    charge_travail: 2
  }}
);

db.utilisateurs.updateOne(
  {email: 'Doc2@gmail.com'},
  {$set: {
    department_id: pneumoId,
    specialite: 'pneumologie', 
    charge_travail: 1
  }}
);

// 4. Assigner le patient au département de cardiologie (sans médecin assigné)
db.utilisateurs.updateOne(
  {email: 'testP1@gmail.com'},
  {$set: {
    department_id: cardioId,
    medecin_assigne: null
  }}
);

// 5. Créer quelques données de santé de test
const patientId = db.utilisateurs.findOne({email: 'testP1@gmail.com'})._id;

db.donnees.insertMany([
  {
    user_id: patientId.toString(),
    type: 'frequence_cardiaque',
    valeur: 75,
    unite: 'bpm',
    timestamp: new Date(),
    source: 'smartwatch'
  },
  {
    user_id: patientId.toString(),
    type: 'pression_arterielle',
    valeur: '120/80',
    unite: 'mmHg',
    timestamp: new Date(),
    source: 'tensiometre'
  }
]);

// 6. Créer une alerte de test
db.alertes.insertOne({
  user_id: patientId.toString(),
  type: 'frequence_cardiaque_elevee',
  message: 'Fréquence cardiaque élevée détectée',
  statut: 'nouvelle',
  priorite: 'moyenne',
  timestamp: new Date(),
  donnee_source: {
    type: 'frequence_cardiaque',
    valeur: 95
  }
});

print('Données de test créées avec succès!');
print('Technicien: technicien@example.com (password: password)');
print('Patient: testP1@gmail.com (département: Cardiologie, sans médecin assigné)');
print('Médecins: Doc1@gmail.com (Cardiologie), Doc2@gmail.com (Pneumologie)');
