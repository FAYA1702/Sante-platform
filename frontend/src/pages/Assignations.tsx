import React from 'react';
import { useAuth } from '../components/Layout';
import AssignationManager from '../components/AssignationManager';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUserMd, faUsers, faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import { Link } from 'react-router-dom';

const Assignations: React.FC = () => {
  const [authState] = useAuth();
  const { role, username } = authState;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Link
                to="/dashboard"
                className="mr-4 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
              >
                <FontAwesomeIcon icon={faArrowLeft} className="text-xl" />
              </Link>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  <FontAwesomeIcon 
                    icon={role === 'patient' ? faUserMd : faUsers} 
                    className="mr-3 text-blue-600 dark:text-blue-400" 
                  />
                  {role === 'patient' ? 'Mes Médecins' : 'Mes Patients'}
                </h1>
                <p className="mt-2 text-gray-600 dark:text-gray-300">
                  {role === 'patient' 
                    ? 'Gérez vos relations avec vos médecins traitants'
                    : 'Gérez vos patients et leurs suivis médicaux'
                  }
                </p>
              </div>
            </div>
            
            {/* Badge de rôle */}
            <div className="flex items-center">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                role === 'patient' 
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                  : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              }`}>
                {role === 'patient' ? 'Patient' : 'Médecin'}
              </span>
            </div>
          </div>
        </div>

        {/* Instructions selon le rôle */}
        <div className="mb-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">
            {role === 'patient' ? 'Comment ça marche ?' : 'Guide médecin'}
          </h2>
          {role === 'patient' ? (
            <div className="text-blue-800 dark:text-blue-200">
              <p className="mb-2">
                <strong>1. Recherchez un médecin</strong> - Utilisez la barre de recherche pour trouver un médecin par nom, email ou spécialité.
              </p>
              <p className="mb-2">
                <strong>2. Demandez une assignation</strong> - Cliquez sur "Sélectionner" pour envoyer une demande d'assignation.
              </p>
              <p>
                <strong>3. Suivi médical</strong> - Une fois assigné, votre médecin pourra accéder à vos données de santé et vous fournir des recommandations.
              </p>
            </div>
          ) : (
            <div className="text-blue-800 dark:text-blue-200">
              <p className="mb-2">
                <strong>Patients assignés</strong> - Consultez la liste de vos patients et leur historique médical.
              </p>
              <p className="mb-2">
                <strong>Accès aux données</strong> - Vous avez accès aux données de santé, alertes et recommandations de vos patients.
              </p>
              <p>
                <strong>Suivi personnalisé</strong> - Utilisez le tableau de bord médecin pour un suivi détaillé de chaque patient.
              </p>
            </div>
          )}
        </div>

        {/* Statistiques rapides */}
        {role === 'medecin' && (
          <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <FontAwesomeIcon icon={faUsers} className="text-2xl text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Patients actifs
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    -
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <FontAwesomeIcon icon={faUserMd} className="text-2xl text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Consultations ce mois
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    -
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <FontAwesomeIcon icon={faUsers} className="text-2xl text-orange-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Alertes en attente
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    -
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Composant principal de gestion des assignations */}
        <AssignationManager />

        {/* Section d'aide */}
        <div className="mt-8 bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
            Besoin d'aide ?
          </h3>
          <div className="text-gray-600 dark:text-gray-300">
            <p className="mb-2">
              • <strong>Problème d'assignation ?</strong> Contactez le support technique
            </p>
            <p className="mb-2">
              • <strong>Changement de médecin ?</strong> Vous pouvez gérer vos assignations à tout moment
            </p>
            <p>
              • <strong>Confidentialité :</strong> Vos données sont protégées et ne sont accessibles qu'à vos médecins assignés
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Assignations;
