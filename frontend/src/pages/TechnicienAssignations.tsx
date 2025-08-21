import React, { useState, useEffect } from 'react';
import { useAuth } from '../components/Layout';
import { ArrowLeftIcon, UserGroupIcon, StethoscopeIcon, SparklesIcon, CheckIcon, XMarkIcon } from '../components/icons';
import { Link } from 'react-router-dom';
import api from '../api';

interface PatientSansAssignation {
  id: string;
  username: string;
  email: string;
  department_id?: string;
  date_inscription: string;
}

interface MedecinDisponible {
  id: string;
  username: string;
  email: string;
  department_id: string;
  nb_patients: number;
  charge_travail: string;
}

interface AssignationHistorique {
  id: string;
  patient_id: string;
  patient_nom: string;
  medecin_id: string;
  medecin_nom: string;
  date_assignation: string;
  type: string;
  statut: string;
}

const TechnicienAssignations: React.FC = () => {
  const [authState] = useAuth();
  const { role, username, token } = authState;
  
  const [patientsSansAssignation, setPatientsSansAssignation] = useState<PatientSansAssignation[]>([]);
  const [medecinsDisponibles, setMedecinsDisponibles] = useState<MedecinDisponible[]>([]);
  const [historique, setHistorique] = useState<AssignationHistorique[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'patients' | 'medecins' | 'historique'>('patients');
  const [selectedPatient, setSelectedPatient] = useState<string | null>(null);
  const [assignmentLoading, setAssignmentLoading] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  // Garder l'ordre des hooks stable; on rendra l'accès refusé dans le JSX plus bas

  const fetchData = async () => {
    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };
      
      const [patientsRes, medecinsRes, historiqueRes] = await Promise.all([
        api.get('/assignations/patients-sans-assignation', { headers }),
        api.get('/assignations/medecins-disponibles', { headers }),
        api.get('/assignations/historique', { headers })
      ]);
      
      const patientsData = Array.isArray(patientsRes.data)
        ? patientsRes.data
        : (patientsRes.data?.items ?? []);
      const medecinsData = Array.isArray(medecinsRes.data)
        ? medecinsRes.data
        : (medecinsRes.data?.items ?? []);
      const historiqueData = Array.isArray(historiqueRes.data)
        ? historiqueRes.data
        : (historiqueRes.data?.items ?? []);

      setPatientsSansAssignation(patientsData);
      setMedecinsDisponibles(medecinsData);
      setHistorique(historiqueData);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
      setMessage({ type: 'error', text: 'Erreur lors du chargement des données' });
    } finally {
      setLoading(false);
    }
  };

  const assignerPatient = async (patientId: string, medecinId?: string, useIA = false) => {
    try {
      setAssignmentLoading(patientId);
      const headers = { Authorization: `Bearer ${token}` };
      
      const payload = {
        patient_id: patientId,
        medecin_id: useIA ? undefined : medecinId
      };
      
      const response = await api.post('/assignations/assigner', payload, { headers });
      
      if (response.data.success) {
        setMessage({ type: 'success', text: response.data.message });
        await fetchData(); // Recharger les données
        setSelectedPatient(null);
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Erreur lors de l\'assignation' });
    } finally {
      setAssignmentLoading(null);
    }
  };

  useEffect(() => {
    if (role === 'technicien') {
      fetchData();
    }
  }, [role]);

  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => setMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {role !== 'technicien' ? (
          <div className="min-h-[50vh] flex items-center justify-center">
            <div className="text-center">
              <XMarkIcon className="mx-auto h-12 w-12 text-red-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Accès refusé</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Cette page est réservée aux techniciens médicaux.
              </p>
              <div className="mt-6">
                <Link
                  to="/dashboard"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  Retour au tableau de bord
                </Link>
              </div>
            </div>
          </div>
        ) : (
        <>
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Link
                to="/dashboard"
                className="mr-4 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
              >
                <ArrowLeftIcon className="text-xl" />
              </Link>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
                  <UserGroupIcon className="mr-3 text-blue-600 dark:text-blue-400" />
                  Gestion des Assignations
                </h1>
                <p className="mt-2 text-gray-600 dark:text-gray-300">
                  Interface technicien médical pour assigner les patients aux médecins
                </p>
              </div>
            </div>
            
            <div className="flex items-center">
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                Technicien Médical
              </span>
            </div>
          </div>
        </div>

        {/* Messages */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-100 border border-green-400 text-green-700' 
              : 'bg-red-100 border border-red-400 text-red-700'
          }`}>
            <div className="flex">
              {message.type === 'success' ? (
                <CheckIcon className="h-5 w-5 mr-2" />
              ) : (
                <XMarkIcon className="h-5 w-5 mr-2" />
              )}
              {message.text}
            </div>
          </div>
        )}

        {/* Statistiques */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="text-2xl text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Patients sans assignation
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {patientsSansAssignation.length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <StethoscopeIcon className="text-2xl text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Médecins disponibles
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {medecinsDisponibles.length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <SparklesIcon className="text-2xl text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  Assignations aujourd'hui
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {Array.isArray(historique)
                    ? historique.filter(h => (h?.date_assignation || '').startsWith(new Date().toISOString().split('T')[0])).length
                    : 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Onglets */}
        <div className="mb-6">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: 'patients', name: 'Patients sans assignation', count: patientsSansAssignation.length },
              { id: 'medecins', name: 'Médecins disponibles', count: medecinsDisponibles.length },
              { id: 'historique', name: 'Historique', count: Array.isArray(historique) ? historique.length : 0 }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                {tab.name}
                <span className={`ml-2 py-0.5 px-2 rounded-full text-xs ${
                  activeTab === tab.id
                    ? 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300'
                    : 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-300'
                }`}>
                  {tab.count}
                </span>
              </button>
            ))}
          </nav>
        </div>

        {/* Contenu des onglets */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
            {activeTab === 'patients' && (
              <div className="p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Patients sans médecin assigné ({patientsSansAssignation.length})
                </h3>
                {patientsSansAssignation.length === 0 ? (
                  <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                    Tous les patients ont un médecin assigné ✅
                  </p>
                ) : (
                  <div className="space-y-4">
                    {patientsSansAssignation.map((patient) => (
                      <div key={patient.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">{patient.username}</h4>
                            <p className="text-sm text-gray-500 dark:text-gray-400">{patient.email}</p>
                            <p className="text-xs text-gray-400 dark:text-gray-500">
                              Département: {patient.department_id || 'Non spécifié'}
                            </p>
                          </div>
                          <div className="flex space-x-2">
                            <button
                              onClick={() => assignerPatient(patient.id, undefined, true)}
                              disabled={assignmentLoading === patient.id}
                              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                            >
                              {assignmentLoading === patient.id ? (
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                              ) : (
                                <SparklesIcon className="mr-2 h-4 w-4" />
                              )}
                              Assigner par IA
                            </button>
                            <button
                              onClick={() => setSelectedPatient(selectedPatient === patient.id ? null : patient.id)}
                              className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                            >
                              Assigner manuellement
                            </button>
                          </div>
                        </div>
                        
                        {selectedPatient === patient.id && (
                          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                            <h5 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Choisir un médecin:</h5>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                              {medecinsDisponibles.map((medecin) => (
                                <button
                                  key={medecin.id}
                                  onClick={() => assignerPatient(patient.id, medecin.id)}
                                  disabled={assignmentLoading === patient.id}
                                  className="text-left p-3 border border-gray-200 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                                >
                                  <div className="font-medium text-gray-900 dark:text-white">{medecin.username}</div>
                                  <div className="text-sm text-gray-500 dark:text-gray-400">{medecin.department_id}</div>
                                  <div className="text-xs text-gray-400 dark:text-gray-500">
                                    Charge: {medecin.charge_travail} ({medecin.nb_patients} patients)
                                  </div>
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {activeTab === 'medecins' && (
              <div className="p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Médecins disponibles ({medecinsDisponibles.length})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {medecinsDisponibles.map((medecin) => (
                    <div key={medecin.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900 dark:text-white">{medecin.username}</h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          medecin.charge_travail === 'Libre' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                          medecin.charge_travail === 'Faible' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                          medecin.charge_travail === 'Modérée' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' :
                          'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                          {medecin.charge_travail}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{medecin.email}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">{medecin.department_id}</p>
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                        {medecin.nb_patients} patient(s) assigné(s)
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {activeTab === 'historique' && (
              <div className="p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Historique des assignations ({Array.isArray(historique) ? historique.length : 0})
                </h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Patient
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Médecin
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Type
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                          Statut
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {(Array.isArray(historique) ? historique : []).map((assignation) => (
                        <tr key={assignation.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                            {assignation.patient_nom}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                            {assignation.medecin_nom}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              assignation.type.includes('ia') ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                              'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                            }`}>
                              {assignation.type.includes('ia') ? 'IA' : 'Manuel'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                            {new Date(assignation.date_assignation).toLocaleDateString('fr-FR')}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              assignation.statut === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                              'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            }`}>
                              {assignation.statut}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Instructions pour technicien */}
        <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">
            Instructions pour les assignations
          </h3>
          <div className="text-blue-800 dark:text-blue-200">
            <p className="mb-2">
              • <strong>Assignation IA :</strong> L'algorithme analyse le département, la spécialité et la charge de travail pour suggérer le médecin optimal
            </p>
            <p className="mb-2">
              • <strong>Assignation manuelle :</strong> Vous pouvez choisir directement un médecin selon votre expertise
            </p>
            <p>
              • <strong>Conformité RBAC :</strong> Chaque patient ne peut être assigné qu'à un seul médecin référent
            </p>
          </div>
        </div>
        </>
        )}
      </div>
    </div>
  );
};

export default TechnicienAssignations;
