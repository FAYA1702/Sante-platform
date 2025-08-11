// Script pour mettre à jour les statuts des alertes et recommandations
console.log('=== MISE A JOUR STATUTS ===');

console.log('1. Mise à jour des alertes sans statut:');
const alertes_result = db.alertes.updateMany(
  { $or: [
    { statut: { $exists: false } },
    { statut: null },
    { statut: "" }
  ]},
  { $set: { statut: 'nouvelle' } }
);
console.log('Alertes mises à jour:', alertes_result.modifiedCount);

console.log('2. Mise à jour des recommandations sans statut:');
const recos_result = db.recommandations.updateMany(
  { $or: [
    { statut: { $exists: false } },
    { statut: null },
    { statut: "" }
  ]},
  { $set: { statut: 'nouvelle' } }
);
console.log('Recommandations mises à jour:', recos_result.modifiedCount);

console.log('3. Vérification après mise à jour:');
console.log('Alertes avec statut nouvelle:', db.alertes.find({statut: 'nouvelle'}).count());
console.log('Recommandations avec statut nouvelle:', db.recommandations.find({statut: 'nouvelle'}).count());

console.log('4. Test requête médecin:');
const medecin = db.utilisateurs.findOne({email: 'faye@17.com'});
const patient_ids = medecin.patient_ids;
console.log('Patient IDs:', patient_ids);

const alertes_medecin = db.alertes.find({
  'user_id': { $in: patient_ids },
  'statut': 'nouvelle'
}).count();
console.log('Alertes trouvées pour le médecin:', alertes_medecin);

const recos_medecin = db.recommandations.find({
  'user_id': { $in: patient_ids },
  'statut': 'nouvelle'
}).count();
console.log('Recommandations trouvées pour le médecin:', recos_medecin);
