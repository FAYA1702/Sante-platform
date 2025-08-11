import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import CreateRecommandationModal from '../components/CreateRecommandationModal';

interface Patient {
  id: string;
  username: string;
  email: string;
  derniere_connexion?: string;
}

interface Alerte {
  id: string;
  user_id: string;
  message: string;
  niveau: string;
  date: string;
  statut: string;
  patient_nom?: string;
}

interface Recommandation {
  id: string;
  user_id: string;
  titre: string;
  description: string;
  date: string;
  statut: string;
  patient_nom?: string;
}

const MedecinDashboard: React.FC = () => {
  const [showRecoModal, setShowRecoModal] = useState(false);
  const [modalPatient, setModalPatient] = useState<Patient | undefined>(undefined);
  const [modalAlerte, setModalAlerte] = useState<Alerte | undefined>(undefined);

  const [patients, setPatients] = useState<Patient[]>([]);
  const [alertes, setAlertes] = useState<Alerte[]>([]);
  const [recommandations, setRecommandations] = useState<Recommandation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPatient, setSelectedPatient] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchMedecinData();
  }, []);

  const fetchMedecinData = async () => {
    try {
      setLoading(true);
      
      const patientsResponse = await api.get('/medecin/patients');
      setPatients(patientsResponse.data);

      const alertesResponse = await api.get('/medecin/alertes?statut=nouvelle');
      setAlertes(alertesResponse.data);

      const recosResponse = await api.get('/medecin/recommandations?statut=nouvelle');
      setRecommandations(recosResponse.data);

    } catch (error) {
      console.error('Erreur lors du chargement des données médecin:', error);
    } finally {
      setLoading(false);
    }
  };

  const marquerVue = async (type: 'alerte' | 'recommandation', id: string) => {
    try {
      await api.patch(`/${type}s/${id}/marquer-vue`);
      
      if (type === 'alerte') {
        setAlertes(prev => prev.map(a => 
          a.id === id ? { ...a, statut: 'vue' } : a
        ));
      } else {
        setRecommandations(prev => prev.map(r => 
          r.id === id ? { ...r, statut: 'vue' } : r
        ));
      }
    } catch (error) {
      console.error(`Erreur lors du marquage comme vue:`, error);
    }
  };

  const filteredAlertes = selectedPatient 
    ? alertes.filter(a => a.user_id === selectedPatient)
    : alertes;

  const filteredRecommandations = selectedPatient 
    ? recommandations.filter(r => r.user_id === selectedPatient)
    : recommandations;

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Handler création reco
  const handleCreateReco = async (values: { user_id: string; titre: string; description: string }) => {
    try {
      await api.post('/medecin/recommandations', values);
      setShowRecoModal(false);
      fetchMedecinData();
    } catch (e) {
      alert('Erreur lors de la création de la recommandation');
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* En-tête */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          🏥 Télésurveillance Médicale
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Surveillance à distance de vos patients • Alertes IA en temps réel
        </p>
      </div>

      {/* Filtre patient */}
      <div className="mb-6 flex flex-wrap gap-4 items-center">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            📋 Patient suivi :
          </label>
          <select
            value={selectedPatient}
            onChange={(e) => setSelectedPatient(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Vue d'ensemble de mes patients</option>
            {patients.map(patient => (
              <option key={patient.id} value={patient.id}>
                {patient.username}
              </option>
            ))}
          </select>
        </div>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          💡 Sélectionnez un patient pour un suivi détaillé
        </div>
      </div>

      {/* Statistiques */}

      {/* Modal création recommandation */}
      <CreateRecommandationModal
        open={showRecoModal}
        onClose={() => setShowRecoModal(false)}
        onSubmit={handleCreateReco}
        patient={modalPatient}
        alerte={modalAlerte}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Patients Suivis</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{patients.length}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Télésurveillance active</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
              <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 18.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">🚨 Alertes IA</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{filteredAlertes.filter(a => a.statut === 'nouvelle').length}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Nouvelles détections</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">🤖 Recommandations IA</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{filteredRecommandations.filter(r => r.statut === 'nouvelle').length}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Suggestions automatiques</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <svg className="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 18.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">⚠️ Urgences</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{filteredAlertes.filter(a => a.niveau === 'critique').length}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Intervention requise</p>
            </div>
          </div>
        </div>
      </div>

      {/* Alertes et Recommandations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Alertes */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
              <svg className="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 18.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              🚨 Alertes de Télésurveillance ({filteredAlertes.filter(a => a.statut === 'nouvelle').length})
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Détections automatiques IA sur les paramètres vitaux
            </p>
          </div>
          <div className="p-6 max-h-96 overflow-y-auto">
            {filteredAlertes.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                Aucune alerte nouvelle
              </p>
            ) : (
              <div className="space-y-4">
                {filteredAlertes.map(alerte => (
                  <div
                    key={alerte.id}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      alerte.statut === 'nouvelle' 
                        ? 'border-red-200 bg-red-50 dark:bg-red-900/20 dark:border-red-800' 
                        : 'border-gray-200 bg-gray-50 dark:bg-gray-700 dark:border-gray-600'
                    }`}
                    onClick={() => {
                      if (alerte.statut === 'nouvelle') {
                        marquerVue('alerte', alerte.id);
                      }
                      navigate(`/patients/${alerte.user_id}`);
                    }}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        alerte.niveau === 'critical' 
                          ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                      }`}>
                        {alerte.niveau === 'critical' ? 'Critique' : 'Attention'}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(alerte.date).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-900 dark:text-white font-medium mb-1">
                      {alerte.patient_nom || 'Patient inconnu'}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {alerte.message}
                    </p>
                    {alerte.statut === 'nouvelle' && (
                      <div className="mt-2">
                        <span className="inline-flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full">
                          <span className="w-2 h-2 bg-blue-400 rounded-full mr-1 animate-pulse"></span>
                          Nouvelle
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recommandations */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              🤖 Recommandations IA ({filteredRecommandations.filter(r => r.statut === 'nouvelle').length})
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Suggestions diagnostiques générées automatiquement
            </p>
          </div>
          <div className="p-6 max-h-96 overflow-y-auto">
            {filteredRecommandations.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                Aucune recommandation nouvelle
              </p>
            ) : (
              <div className="space-y-4">
                {filteredRecommandations.map(reco => (
                  <div
                    key={reco.id}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      reco.statut === 'nouvelle' 
                        ? 'border-green-200 bg-green-50 dark:bg-green-900/20 dark:border-green-800' 
                        : 'border-gray-200 bg-gray-50 dark:bg-gray-700 dark:border-gray-600'
                    }`}
                    onClick={() => {
                      if (reco.statut === 'nouvelle') {
                        marquerVue('recommandation', reco.id);
                      }
                      navigate(`/patients/${reco.user_id}`);
                    }}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(reco.date).toLocaleDateString('fr-FR')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-900 dark:text-white font-medium mb-1">
                      {reco.patient_nom || 'Patient inconnu'}
                    </p>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                      {reco.titre}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {reco.description}
                    </p>
                    {reco.statut === 'nouvelle' && (
                      <div className="mt-2">
                        <span className="inline-flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full">
                          <span className="w-2 h-2 bg-blue-400 rounded-full mr-1 animate-pulse"></span>
                          Nouvelle
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Alertes IA */}
      <div className="mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
              <svg className="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636a9 9 0 11-12.728 0M12 3v9" />
              </svg>
              Alertes IA récentes
            </h2>
          </div>
          <div className="p-6">
            {filteredAlertes.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                Aucune alerte récente
              </p>
            ) : (
              <div className="space-y-4">
                {filteredAlertes.map(alerte => (
                  <div
                    key={alerte.id}
                    className="p-4 border border-red-200 dark:border-red-600 rounded-lg bg-red-50 dark:bg-red-900/30 flex flex-col md:flex-row md:items-center md:justify-between"
                  >
                    <div>
                      <div className="flex items-center mb-1">
                        <span className={`inline-flex items-center px-2 py-1 text-xs rounded-full mr-2 ${alerte.niveau === 'critical' ? 'bg-red-500 text-white' : 'bg-yellow-200 text-yellow-800'}`}>
                          {alerte.niveau === 'critical' ? 'Critique' : 'Alerte'}
                        </span>
                        <span className="font-medium text-gray-800 dark:text-white">{alerte.message}</span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-300">{alerte.patient_nom || ''} • {new Date(alerte.date).toLocaleString()}</p>
                    </div>
                    <div className="mt-3 md:mt-0 md:ml-6 flex items-center gap-2">
                      <button
                        className="px-3 py-1 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold"
                        onClick={() => {
                          const patient = patients.find(p => p.id === alerte.user_id);
                          setModalPatient(patient);
                          setModalAlerte(alerte);
                          setShowRecoModal(true);
                        }}
                      >
                        Créer une recommandation
                      </button>
                      <button
                        className="px-2 py-1 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 text-xs"
                        onClick={() => marquerVue('alerte', alerte.id)}
                      >
                        Marquer comme vue
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MedecinDashboard;
