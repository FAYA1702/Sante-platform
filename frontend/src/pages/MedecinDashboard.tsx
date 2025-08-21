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
      // Auto-sélectionner le premier patient si aucun n'est sélectionné
      if (!selectedPatient && Array.isArray(patientsResponse.data) && patientsResponse.data.length > 0) {
        setSelectedPatient(patientsResponse.data[0].id);
      }
      console.debug('[MedecinDashboard] patients =>', patientsResponse.data);

      // Récupérer TOUTES les alertes (pas seulement les nouvelles)
      const alertesResponse = await api.get('/medecin/alertes');
      const rawAlertes = Array.isArray(alertesResponse.data) ? alertesResponse.data : [];
      const normalizedAlertes = rawAlertes.map((a: any) => ({
        ...a,
        // uniformiser l'id patient et le statut/niveau
        user_id: a.user_id ?? a.patient_id ?? a.userId ?? a.patientId,
        statut: (a.statut || '').toLowerCase(),
        niveau: (a.niveau || '').toLowerCase(),
      }));
      setAlertes(normalizedAlertes);
      console.debug('[MedecinDashboard] alertes =>', normalizedAlertes);

      const recosResponse = await api.get('/medecin/recommandations');
      const rawRecos = Array.isArray(recosResponse.data) ? recosResponse.data : [];
      const normalizedRecos = rawRecos.map((r: any) => ({
        ...r,
        user_id: r.user_id ?? r.patient_id ?? r.userId ?? r.patientId,
        statut: (r.statut || '').toLowerCase(),
      }));
      setRecommandations(normalizedRecos);
      console.debug('[MedecinDashboard] recommandations =>', normalizedRecos);

    } catch (error) {
      console.error('Erreur lors du chargement des données médecin:', error);
    } finally {
      setLoading(false);
    }
  };

  // Helper: une reco est considérée "nouvelle" si statut = active/nouvelle, ou is_active=true, ou statut absent
  const isNewReco = (r: Partial<Recommandation> & { is_active?: boolean }) => {
    const s = (r.statut || '').toLowerCase();
    return r.is_active === true || s === 'active' || s === 'nouvelle' || !r.statut;
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
  const handleCreateReco = async (values: { patient_id: string; titre: string; description: string; alerte_id?: string }) => {
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
        <div className="bg-white/70 dark:bg-gray-900/60 rounded-xl shadow ring-1 ring-sky-100 dark:ring-sky-900 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <i className="bi bi-people text-blue-600 dark:text-blue-400 text-xl"></i>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Patients Suivis</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{patients.length}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Télésurveillance active</p>
            </div>
          </div>
        </div>

        <div className="bg-white/70 dark:bg-gray-900/60 rounded-xl shadow ring-1 ring-sky-100 dark:ring-sky-900 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
              <i className="bi bi-bell text-red-600 dark:text-red-400 text-xl"></i>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Alertes IA</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{filteredAlertes.filter(a => ['nouvelle','nouveau','new'].includes((a.statut || '').toLowerCase())).length}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Nouvelles détections</p>
            </div>
          </div>
        </div>

        <div className="bg-white/70 dark:bg-gray-900/60 rounded-xl shadow ring-1 ring-sky-100 dark:ring-sky-900 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <i className="bi bi-robot text-green-600 dark:text-green-400 text-xl"></i>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Recommandations IA</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{filteredRecommandations.filter(r => ['active','nouvelle'].includes((r.statut || '').toLowerCase())).length}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Suggestions automatiques</p>
            </div>
          </div>
        </div>

        <div className="bg-white/70 dark:bg-gray-900/60 rounded-xl shadow ring-1 ring-sky-100 dark:ring-sky-900 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <i className="bi bi-exclamation-octagon text-yellow-600 dark:text-yellow-400 text-xl"></i>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">⚠️ Urgences</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{filteredAlertes.filter(a => ['critique','critical'].includes((a.niveau || '').toLowerCase())).length}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Intervention requise</p>
            </div>
          </div>
        </div>
      </div>

      {/* Alertes et Recommandations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Alertes */}
        <div className="bg-white/70 dark:bg-gray-900/60 rounded-xl shadow ring-1 ring-sky-100 dark:ring-sky-900">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
              <i className="bi bi-bell-fill text-red-500 mr-2"></i>
              🚨 Alertes de Télésurveillance ({filteredAlertes.filter(a => ['nouvelle','nouveau','new'].includes((a.statut || '').toLowerCase())).length})
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Détections automatiques IA sur les paramètres vitaux
            </p>
          </div>
          <div className="p-6 max-h-96 overflow-y-auto">
            {filteredAlertes.length === 0 ? (
              <div className="text-gray-500 dark:text-gray-400 text-center py-8 space-y-2">
                <p>Aucune alerte nouvelle</p>
                <p className="text-xs">Astuce: vérifiez que des patients vous sont assignés et que l'API renvoie des alertes pour ces patients.</p>
              </div>
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
                    }}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        ['critique','critical'].includes((alerte.niveau || '').toLowerCase())
                          ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                      }`}>
                        {['critique','critical'].includes((alerte.niveau || '').toLowerCase()) ? 'Critique' : 'Attention'}
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
                      <div className="mt-3 flex gap-2">
                        <span className="inline-flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full">
                          <span className="w-2 h-2 bg-blue-400 rounded-full mr-1 animate-pulse"></span>
                          Nouvelle
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            const patient = patients.find(p => p.id === alerte.user_id);
                            if (patient) {
                              setModalPatient(patient);
                              setModalAlerte(alerte);
                              setShowRecoModal(true);
                            }
                          }}
                          className="inline-flex items-center px-3 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full hover:bg-green-200 dark:hover:bg-green-800 transition-colors"
                        >
                          ✚ Créer recommandation
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recommandations */}
        <div className="bg-white/70 dark:bg-gray-900/60 rounded-xl shadow ring-1 ring-sky-100 dark:ring-sky-900 p-6">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
              <i className="bi bi-lightbulb-fill text-green-500 mr-2"></i>
              🤖 Recommandations IA ({filteredRecommandations.filter(r => ['active','nouvelle'].includes((r.statut || '').toLowerCase())).length})
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
                      ['active','nouvelle'].includes((reco.statut || '').toLowerCase()) 
                        ? 'border-green-200 bg-green-50 dark:bg-green-900/20 dark:border-green-800' 
                        : 'border-gray-200 bg-gray-50 dark:bg-gray-700 dark:border-gray-600'
                    }`}
                    onClick={() => {
                      if (['active','nouvelle'].includes((reco.statut || '').toLowerCase())) {
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
                    {['active','nouvelle'].includes((reco.statut || '').toLowerCase()) && (
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

      
    </div>
  );
};

export default MedecinDashboard;
