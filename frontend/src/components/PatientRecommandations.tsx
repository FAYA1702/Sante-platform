import { useEffect, useState } from 'react';
import api from '../api';

interface Recommandation {
  id: string;
  titre: string;
  description: string;
  priorite: string;
  statut: string;
  type: string;
  date_creation: string;
  medecin: {
    nom: string;
    department: string;
  };
  alerte_liee: boolean;
  vue_patient: boolean;
}

interface NotificationInfo {
  non_lues: number;
  total: number;
}

export default function PatientRecommandations() {
  const [recommandations, setRecommandations] = useState<Recommandation[]>([]);
  const [notifications, setNotifications] = useState<NotificationInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statutFiltre, setStatutFiltre] = useState('active');

  useEffect(() => {
    loadRecommandations();
    loadNotifications();
  }, [statutFiltre]);

  const loadRecommandations = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/patient/recommandations?statut=${statutFiltre}&limit=20`);
      setRecommandations(response.data.recommandations || []);
      setError('');
    } catch (err: any) {
      console.error('Erreur lors du chargement des recommandations:', err);
      setError('Impossible de charger les recommandations');
    } finally {
      setLoading(false);
    }
  };

  const loadNotifications = async () => {
    try {
      const response = await api.get('/patient/notifications/recommandations');
      setNotifications(response.data);
    } catch (err: any) {
      console.error('Erreur lors du chargement des notifications:', err);
    }
  };

  const updateStatutRecommandation = async (recommandationId: string, nouveauStatut: string) => {
    try {
      await api.put(`/patient/recommandations/${recommandationId}/statut?nouveau_statut=${nouveauStatut}`);
      
      // Mettre à jour localement
      setRecommandations(prev => 
        prev.map(r => 
          r.id === recommandationId 
            ? { ...r, statut: nouveauStatut }
            : r
        )
      );
      
      // Recharger si on filtre par statut
      if (statutFiltre !== 'all') {
        loadRecommandations();
      }
    } catch (err: any) {
      console.error('Erreur lors de la mise à jour du statut:', err);
      alert('Erreur lors de la mise à jour du statut');
    }
  };

  const getPrioriteColor = (priorite: string) => {
    switch (priorite) {
      case 'critique': return 'bg-red-100 text-red-800 border-red-200';
      case 'haute': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'moyenne': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatutColor = (statut: string) => {
    switch (statut) {
      case 'active': return 'bg-blue-100 text-blue-800';
      case 'en_cours': return 'bg-yellow-100 text-yellow-800';
      case 'terminee': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    if (type.includes('cardiaque')) return '❤️';
    if (type.includes('respiratoire')) return '🫁';
    if (type.includes('tensionnelle')) return '🩺';
    if (type.includes('automatique')) return '🤖';
    return '💡';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Chargement des recommandations...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header avec notifications */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <i className="bi bi-clipboard-check text-blue-600 text-xl"></i>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Mes Recommandations</h2>
              <p className="text-gray-600">Conseils et recommandations de votre médecin</p>
            </div>
          </div>
          
          {notifications && notifications.non_lues > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <i className="bi bi-bell-fill text-red-500"></i>
                <span className="text-red-700 font-medium">
                  {notifications.non_lues} nouvelle(s) recommandation(s)
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Filtres */}
        <div className="flex gap-2 mb-4">
          {['active', 'en_cours', 'terminee', 'all'].map(statut => (
            <button
              key={statut}
              onClick={() => setStatutFiltre(statut)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                statutFiltre === statut
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {statut === 'all' ? 'Toutes' : 
               statut === 'active' ? 'Actives' :
               statut === 'en_cours' ? 'En cours' : 'Terminées'}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Liste des recommandations */}
      <div className="space-y-4">
        {recommandations.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <i className="bi bi-clipboard-check text-gray-400 text-4xl mb-4"></i>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune recommandation</h3>
            <p className="text-gray-600">
              {statutFiltre === 'active' 
                ? 'Vous n\'avez aucune recommandation active pour le moment.'
                : `Aucune recommandation avec le statut "${statutFiltre}".`
              }
            </p>
          </div>
        ) : (
          recommandations.map((reco) => (
            <div key={reco.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
              <div className="p-6">
                {/* Header de la recommandation */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start gap-3">
                    <div className="text-2xl">{getTypeIcon(reco.type)}</div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {reco.titre}
                      </h3>
                      <div className="flex items-center gap-3 text-sm text-gray-600">
                        <span>Dr. {reco.medecin.nom}</span>
                        <span>•</span>
                        <span>{reco.medecin.department}</span>
                        <span>•</span>
                        <span>{new Date(reco.date_creation).toLocaleDateString('fr-FR')}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPrioriteColor(reco.priorite)}`}>
                      {reco.priorite}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatutColor(reco.statut)}`}>
                      {reco.statut === 'active' ? 'Active' :
                       reco.statut === 'en_cours' ? 'En cours' : 'Terminée'}
                    </span>
                    {reco.alerte_liee && (
                      <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                        <i className="bi bi-exclamation-triangle mr-1"></i>
                        Alerte
                      </span>
                    )}
                  </div>
                </div>

                {/* Description */}
                <div className="mb-4">
                  <p className="text-gray-700 whitespace-pre-line">{reco.description}</p>
                </div>

                {/* Actions */}
                {reco.statut === 'active' && (
                  <div className="flex gap-2 pt-4 border-t border-gray-100">
                    <button
                      onClick={() => updateStatutRecommandation(reco.id, 'en_cours')}
                      className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-sm"
                    >
                      <i className="bi bi-play-circle mr-1"></i>
                      Commencer
                    </button>
                    <button
                      onClick={() => updateStatutRecommandation(reco.id, 'terminee')}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                    >
                      <i className="bi bi-check-circle mr-1"></i>
                      Marquer comme terminée
                    </button>
                  </div>
                )}

                {reco.statut === 'en_cours' && (
                  <div className="flex gap-2 pt-4 border-t border-gray-100">
                    <button
                      onClick={() => updateStatutRecommandation(reco.id, 'terminee')}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                    >
                      <i className="bi bi-check-circle mr-1"></i>
                      Marquer comme terminée
                    </button>
                    <button
                      onClick={() => updateStatutRecommandation(reco.id, 'active')}
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
                    >
                      <i className="bi bi-arrow-clockwise mr-1"></i>
                      Remettre active
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
