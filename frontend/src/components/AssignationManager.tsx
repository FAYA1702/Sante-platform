import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faUserMd, 
  faUsers, 
  faBuilding,
  faFilter,
  faRobot,
  faCheck,
  faTimes,
  faSpinner,
  faExclamationTriangle,
  faEye
} from '@fortawesome/free-solid-svg-icons';

interface Department {
  id: string;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
}

interface Referral {
  id: string;
  patient_id: string;
  proposed_department_id: string;
  status: 'pending' | 'accepted' | 'rejected';
  source: 'IA' | 'manual';
  notes?: string;
  created_at: string;
  patient_name?: string;
  department_name?: string;
  created_by_name?: string;
}

interface Assignment {
  id: string;
  patient_id: string;
  department_id: string;
  doctor_id: string;
  status: 'active' | 'ended' | 'suspended';
  notes?: string;
  start_at: string;
  end_at?: string;
  patient_name?: string;
  department_name?: string;
  doctor_name?: string;
}

const AssignationManager: React.FC = () => {
  const [authState, logout] = useAuth();
  const { isAuthenticated, role, username, token } = authState;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // États pour les données
  const [departments, setDepartments] = useState<Department[]>([]);
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  
  // États pour les filtres
  const [selectedDepartment, setSelectedDepartment] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'assignments' | 'referrals' | 'auto-assignments'>('assignments');

  const apiHeaders = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  // Charger les départements
  const loadDepartments = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/departments`, {
        headers: apiHeaders
      });
      if (response.ok) {
        const data = await response.json();
        setDepartments(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des départements:', error);
    }
  };

  // Charger les orientations (referrals)
  const loadReferrals = async () => {
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.append('status_filter', statusFilter);
      if (selectedDepartment) params.append('department_id', selectedDepartment);
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/referrals?${params}`, {
        headers: apiHeaders
      });
      if (response.ok) {
        const data = await response.json();
        setReferrals(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des orientations:', error);
    }
  };

  // Charger les assignations
  const loadAssignments = async () => {
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.append('status_filter', statusFilter);
      if (selectedDepartment) params.append('department_id', selectedDepartment);
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/assignments?${params}`, {
        headers: apiHeaders
      });
      if (response.ok) {
        const data = await response.json();
        setAssignments(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des assignations:', error);
    }
  };

  // Traiter une orientation (accepter/refuser)
  const handleReferralAction = async (referralId: string, action: 'accepted' | 'rejected', notes?: string) => {
    try {
      setLoading(true);
      const response = await fetch(`${import.meta.env.VITE_API_URL}/referrals/${referralId}`, {
        method: 'PATCH',
        headers: apiHeaders,
        body: JSON.stringify({
          status: action,
          notes: notes
        })
      });
      
      if (response.ok) {
        setSuccess(`Orientation ${action === 'accepted' ? 'acceptée' : 'refusée'} avec succès`);
        await loadReferrals();
        await loadAssignments();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors du traitement de l\'orientation');
      }
    } catch (error) {
      setError('Erreur lors du traitement de l\'orientation');
    } finally {
      setLoading(false);
    }
  };

  // Charger les données au montage du composant
  useEffect(() => {
    if (token) {
      loadDepartments();
      loadReferrals();
      loadAssignments();
    }
  }, [token, statusFilter, selectedDepartment]);

  // Effacer les messages après 5 secondes
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError(null);
        setSuccess(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <FontAwesomeIcon icon={faSpinner} spin className="text-3xl text-blue-600" />
        <span className="ml-3 text-lg text-gray-600 dark:text-gray-300">Chargement...</span>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          <FontAwesomeIcon icon={faBuilding} className="mr-3 text-blue-600" />
          Gestion des Assignations par Département
        </h2>
        <p className="text-gray-600 dark:text-gray-300">
          Gérez les orientations et assignations médicales avec filtrage par département
        </p>
      </div>

      {/* Messages d'état */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          <FontAwesomeIcon icon={faTimes} className="mr-2" />
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
          <FontAwesomeIcon icon={faCheck} className="mr-2" />
          {success}
        </div>
      )}

      {/* Filtres */}
      <div className="mb-6 bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
        <div className="flex flex-wrap gap-4">
          {/* Filtre par département */}
          <div className="flex-1 min-w-48">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <FontAwesomeIcon icon={faBuilding} className="mr-2" />
              Département
            </label>
            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:text-white"
            >
              <option value="">Tous les départements</option>
              {departments.map((dept) => (
                <option key={dept.id} value={dept.id}>
                  {dept.name} ({dept.code})
                </option>
              ))}
            </select>
          </div>

          {/* Filtre par statut */}
          <div className="flex-1 min-w-48">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <FontAwesomeIcon icon={faFilter} className="mr-2" />
              Statut
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:text-white"
            >
              <option value="">Tous les statuts</option>
              <option value="pending">En attente</option>
              <option value="accepted">Accepté</option>
              <option value="rejected">Refusé</option>
              <option value="active">Actif</option>
              <option value="ended">Terminé</option>
            </select>
          </div>
        </div>
      </div>

      {/* Onglets */}
      <div className="mb-6">
        <div className="border-b border-gray-200 dark:border-gray-600">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('assignments')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'assignments'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <FontAwesomeIcon icon={faUsers} className="mr-2" />
              Assignations ({assignments.length})
            </button>
            <button
              onClick={() => setActiveTab('referrals')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'referrals'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <FontAwesomeIcon icon={faRobot} className="mr-2" />
              Orientations IA ({referrals.length})
            </button>
            {(role === 'admin' || role === 'technicien') && (
              <button
                onClick={() => setActiveTab('auto-assignments')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'auto-assignments'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <FontAwesomeIcon icon={faUsers} className="mr-2" />
                Attributions Auto
              </button>
            )}
          </nav>
        </div>
      </div>

      {/* Contenu des onglets */}
      {activeTab === 'assignments' && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Assignations Actives
          </h3>
          
          {assignments.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <FontAwesomeIcon icon={faUsers} className="text-4xl mb-4" />
              <p>Aucune assignation trouvée</p>
            </div>
          ) : (
            <div className="space-y-4">
              {assignments.map((assignment) => (
                <div key={assignment.id} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900 dark:text-white">
                        {assignment.patient_name}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        <FontAwesomeIcon icon={faBuilding} className="mr-1" />
                        {assignment.department_name}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        <FontAwesomeIcon icon={faUserMd} className="mr-1" />
                        Dr. {assignment.doctor_name}
                      </p>
                    </div>
                    
                    <div className="text-right">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        assignment.status === 'active' 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : assignment.status === 'ended'
                          ? 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                      }`}>
                        {assignment.status === 'active' ? 'Actif' : 
                         assignment.status === 'ended' ? 'Terminé' : 'Suspendu'}
                      </span>
                      <p className="text-xs text-gray-500 mt-1">
                        Depuis: {new Date(assignment.start_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  
                  {assignment.notes && (
                    <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
                      <strong>Notes:</strong> {assignment.notes}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'referrals' && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Orientations Proposées par l'IA
          </h3>
          
          {referrals.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <FontAwesomeIcon icon={faRobot} className="text-4xl mb-4" />
              <p>Aucune orientation trouvée</p>
            </div>
          ) : (
            <div className="space-y-4">
              {referrals.map((referral) => (
                <div key={referral.id} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <h4 className="font-semibold text-gray-900 dark:text-white mr-2">
                          {referral.patient_name}
                        </h4>
                        {referral.source === 'IA' && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full text-xs font-medium">
                            <FontAwesomeIcon icon={faRobot} className="mr-1" />
                            IA
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        <FontAwesomeIcon icon={faBuilding} className="mr-1" />
                        Vers: {referral.department_name}
                      </p>
                      <p className="text-xs text-gray-500">
                        Créé le: {new Date(referral.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        referral.status === 'pending' 
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                          : referral.status === 'accepted'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                      }`}>
                        {referral.status === 'pending' ? 'En attente' : 
                         referral.status === 'accepted' ? 'Accepté' : 'Refusé'}
                      </span>
                      
                      {referral.status === 'pending' && role === 'medecin' && (
                        <div className="flex space-x-1">
                          <button
                            onClick={() => handleReferralAction(referral.id, 'accepted')}
                            className="px-2 py-1 bg-green-500 hover:bg-green-600 text-white rounded text-xs"
                            disabled={loading}
                          >
                            <FontAwesomeIcon icon={faCheck} />
                          </button>
                          <button
                            onClick={() => handleReferralAction(referral.id, 'rejected')}
                            className="px-2 py-1 bg-red-500 hover:bg-red-600 text-white rounded text-xs"
                            disabled={loading}
                          >
                            <FontAwesomeIcon icon={faTimes} />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {referral.notes && (
                    <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
                      <strong>Notes:</strong> {referral.notes}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Onglet Attributions Automatiques (Admin/Technicien uniquement) */}
      {activeTab === 'auto-assignments' && (role === 'admin' || role === 'technicien') && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              <FontAwesomeIcon icon={faRobot} className="mr-2 text-blue-600" />
              Attributions Automatiques Récentes
            </h3>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Gestion des attributions IA patient-médecin
            </div>
          </div>

          {/* Statistiques rapides */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center">
                <FontAwesomeIcon icon={faUsers} className="text-2xl text-blue-600 mr-3" />
                <div>
                  <p className="text-sm text-blue-600 dark:text-blue-400 font-medium">Attributions Actives</p>
                  <p className="text-xl font-bold text-blue-900 dark:text-blue-100">
                    {assignments.filter(a => a.status === 'active').length}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
              <div className="flex items-center">
                <FontAwesomeIcon icon={faCheck} className="text-2xl text-green-600 mr-3" />
                <div>
                  <p className="text-sm text-green-600 dark:text-green-400 font-medium">Orientations Acceptées</p>
                  <p className="text-xl font-bold text-green-900 dark:text-green-100">
                    {referrals.filter(r => r.status === 'accepted').length}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
              <div className="flex items-center">
                <FontAwesomeIcon icon={faExclamationTriangle} className="text-2xl text-yellow-600 mr-3" />
                <div>
                  <p className="text-sm text-yellow-600 dark:text-yellow-400 font-medium">En Attente</p>
                  <p className="text-xl font-bold text-yellow-900 dark:text-yellow-100">
                    {referrals.filter(r => r.status === 'pending').length}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Liste des attributions récentes */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
              Attributions Récentes (Dernières 24h)
            </h4>
            
            {assignments.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                <FontAwesomeIcon icon={faUsers} className="text-4xl mb-4" />
                <p>Aucune attribution récente</p>
                <p className="text-sm mt-2">Les nouvelles attributions automatiques apparaîtront ici</p>
              </div>
            ) : (
              <div className="space-y-3">
                {assignments.slice(0, 10).map((assignment) => (
                  <div key={assignment.id} className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <span className="font-medium text-gray-900 dark:text-white mr-2">
                            {assignment.patient_name}
                          </span>
                          <FontAwesomeIcon icon={faUsers} className="text-gray-400 mx-2" />
                          <span className="font-medium text-blue-600 dark:text-blue-400">
                            Dr. {assignment.doctor_name}
                          </span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                          <FontAwesomeIcon icon={faBuilding} className="mr-1" />
                          <span className="mr-4">{assignment.department_name}</span>
                          <span className="text-xs">
                            Attribué le: {new Date(assignment.start_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          assignment.status === 'active' 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : assignment.status === 'ended'
                            ? 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        }`}>
                          {assignment.status === 'active' ? 'Actif' : 
                           assignment.status === 'ended' ? 'Terminé' : 'Suspendu'}
                        </span>
                        
                        {assignment.status === 'active' && (
                          <button
                            onClick={() => {
                              // Fonction pour voir les détails ou modifier l'attribution
                              console.log('Voir détails attribution:', assignment.id);
                            }}
                            className="px-2 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-xs"
                            title="Voir les détails"
                          >
                            <FontAwesomeIcon icon={faEye} />
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {assignment.notes && (
                      <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
                        <strong>Notes:</strong> {assignment.notes}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Actions rapides pour les admins */}
          <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
            <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-3">
              Actions Rapides (Admin)
            </h4>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => {
                  // Fonction pour forcer une réattribution globale
                  console.log('Réattribution globale demandée');
                }}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium"
              >
                <FontAwesomeIcon icon={faRobot} className="mr-2" />
                Réattribution IA Globale
              </button>
              
              <button
                onClick={() => {
                  // Fonction pour équilibrer les charges
                  console.log('Équilibrage des charges demandé');
                }}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium"
              >
                <FontAwesomeIcon icon={faUsers} className="mr-2" />
                Équilibrer les Charges
              </button>
              
              <button
                onClick={() => {
                  // Fonction pour voir les statistiques détaillées
                  console.log('Statistiques détaillées demandées');
                }}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg text-sm font-medium"
              >
                <FontAwesomeIcon icon={faEye} className="mr-2" />
                Statistiques Détaillées
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AssignationManager;
