import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import StatsCard from '../components/StatsCard';
import RecommendationCard from '../components/RecommendationCard';
import HealthChart from '../components/HealthChart';
import AdminApproval from '../components/AdminApproval';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faHeartPulse, 
  faLungs, 
  faRefresh, 
  faChartLine,
  faExclamationTriangle,
  faCheckCircle,
  faBell,
  faCalendarAlt,
  faStethoscope
} from '@fortawesome/free-solid-svg-icons';

interface Alerte {
  id: string;
  user_id: string;
  message: string;
  niveau: string;
  date: string;
}

interface Recommendation {
  id: string;
  titre: string;
  description: string;
  date: string;
  contenu?: string;
}

interface DonneeSante {
  date: string;
  frequence_cardiaque: number;
  taux_oxygene: number;
}

interface Stats {
  total_appareils: number;
  total_donnees: number;
  total_alertes: number;
  total_recommandations: number;
  total_utilisateurs: number;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [alertes, setAlertes] = useState<Alerte[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState('');
  const [donnees, setDonnees] = useState<DonneeSante[]>([]);
  const [recommandations, setRecommandations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingRecos, setLoadingRecos] = useState(true);
  const [recoError, setRecoError] = useState('');

  // Récupérer le nom utilisateur depuis le JWT
  let username = '';
  let role = '';
  try {
    const token = localStorage.getItem('token');
    if (token) {
      const payload = JSON.parse(atob(token.split('.')[1]));
      username = payload.username || '';
      role = payload.role || '';
    }
    if (!username) username = 'Utilisateur';
  } catch (e) {
    console.error('Erreur décodage token:', e);
  }

  const roleColor = role === 'admin' ? 'red' : role === 'medecin' ? 'green' : role === 'technicien' ? 'yellow' : 'blue';
  const roleLabel = role === 'admin' ? 'Administrateur' : role === 'medecin' ? 'Docteur' : role === 'technicien' ? 'Technicien' : 'Patient';

  useEffect(() => {
    // 1. Abonnement aux alertes en temps réel
    const es = new EventSource(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/alerts/stream`, {
      withCredentials: false,
    });

    es.onmessage = (e) => {
      try {
        const message = JSON.parse(e.data);
        
        switch (message.type) {
          case 'alert':
            const alerte = {
              id: message.id,
              user_id: message.user_id,
              message: message.message,
              niveau: message.niveau,
              date: message.date
            };
            setAlertes((prev) => [alerte, ...prev]);
            window.dispatchEvent(new CustomEvent('new-alert', { detail: alerte }));
            console.log('🚨 Nouvelle alerte reçue:', message.message);
            break;
            
          case 'heartbeat':
            console.debug('❤️ SSE Heartbeat reçu');
            break;
            
          case 'error':
            console.error('❌ Erreur SSE:', message.message);
            setError(`Erreur de streaming: ${message.message}`);
            break;
            
          default:
            if (message.message && message.niveau) {
              const alerte = {
                id: message.id || Date.now().toString(),
                user_id: message.user_id || '',
                message: message.message,
                niveau: message.niveau,
                date: message.date || new Date().toISOString()
              };
              setAlertes((prev) => [alerte, ...prev]);
              window.dispatchEvent(new CustomEvent('new-alert', { detail: alerte }));
            }
            break;
        }
      } catch (e) {
        console.error('Erreur de parsing SSE:', e);
        setError('Erreur de communication avec le serveur');
      }
    };

    es.onerror = (event) => {
      console.warn('⚠️ SSE alerts déconnecté:', event);
      setError('Connexion aux alertes interrompue');
      es.close();
    };
    
    es.onopen = () => {
      console.log('✅ Connexion SSE établie');
      setError('');
    };

    // 2. Chargement des statistiques
    (async () => {
      try {
        const { data } = await api.get('/stats');
        setStats(data);
      } catch (e) {
        console.error('Erreur stats', e);
        setError('Impossible de charger les statistiques.');
      }
    })();

    // 3. Chargement des recommandations
    (async () => {
      try {
        setLoadingRecos(true);
        const { data: recos } = await api.get('/recommendations');
        
        const formattedRecos = recos.map((reco: any) => ({
          ...reco,
          titre: reco.titre || reco.contenu?.split('\n')[0]?.substring(0, 50) || 'Sans titre',
          description: reco.description || reco.contenu?.substring(reco.contenu.indexOf('\n') + 1) || 'Aucune description disponible',
        }));
        
        setRecommandations(formattedRecos);
      } catch (err: any) {
        console.error('Erreur lors du chargement des recommandations:', err);
        setRecoError('Impossible de charger les recommandations.');
      } finally {
        setLoadingRecos(false);
      }
    })();

    // 4. Chargement des données de santé
    (async () => {
      try {
        const { data } = await api.get('/data');
        setDonnees(data);
      } catch (e) {
        console.error('Erreur données santé', e);
      }
    })();

    // 5. Chargement des alertes existantes
    (async () => {
      try {
        const { data } = await api.get('/alerts');
        setAlertes(data);
      } catch (e) {
        console.error('Erreur alertes', e);
      } finally {
        setLoading(false);
      }
    })();

    return () => {
      es.close();
    };
  }, []);

  const refreshRecommandations = async () => {
    try {
      setLoadingRecos(true);
      setRecoError('');
      const { data: recos } = await api.get('/recommendations');
      
      const formattedRecos = recos.map((reco: any) => ({
        ...reco,
        titre: reco.titre || reco.contenu?.split('\n')[0]?.substring(0, 50) || 'Sans titre',
        description: reco.description || reco.contenu?.substring(reco.contenu.indexOf('\n') + 1) || 'Aucune description disponible',
      }));
      
      setRecommandations(formattedRecos);
    } catch (err: any) {
      console.error('Erreur lors du rafraîchissement des recommandations:', err);
      setRecoError('Impossible de rafraîchir les recommandations.');
    } finally {
      setLoadingRecos(false);
    }
  };

  const handleAlertClick = (alerte: Alerte) => {
    // Pour un patient connecté, on navigue vers sa propre fiche
    if (role === 'patient') {
      // Récupérer l'ID du patient connecté depuis le JWT (champ 'sub')
      try {
        const token = localStorage.getItem('token');
        if (token) {
          const payload = JSON.parse(atob(token.split('.')[1]));
          const currentUserId = payload.sub; // Le JWT utilise 'sub' pour l'ID utilisateur
          console.log('ID utilisateur depuis JWT:', currentUserId);
          if (currentUserId) {
            navigate(`/patients/${currentUserId}`);
            return;
          }
        }
      } catch (e) {
        console.error('Erreur récupération ID utilisateur:', e);
      }
    }
    
    // Pour médecin/admin, navigation vers le patient de l'alerte
    if (alerte.user_id) {
      navigate(`/patients/${alerte.user_id}`);
    } else {
      console.warn('Alerte sans patient associé:', alerte);
      alert('Cette alerte n\'est pas liée à un patient spécifique.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8 space-y-8">
        
        {/* Header moderne */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-3">
            <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl">
              <FontAwesomeIcon icon={faStethoscope} className="text-white text-2xl" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Tableau de Bord Médical
            </h1>
          </div>
          <p className="text-lg text-slate-600 dark:text-slate-300">
            Bienvenue, <span className="font-semibold text-blue-600 dark:text-blue-400">{username}</span> 
            <span className={`ml-2 px-3 py-1 rounded-full text-sm font-medium bg-${roleColor}-100 text-${roleColor}-700 dark:bg-${roleColor}-900/30 dark:text-${roleColor}-300`}>
              {roleLabel}
            </span>
          </p>
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
            <p className="text-red-700 dark:text-red-300">{error}</p>
          </div>
        )}

        {/* Section Statistiques */}
        {stats && (
          <section className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
                <FontAwesomeIcon icon={faChartLine} className="text-white text-xl" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Vue d'ensemble</h2>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {(role === 'admin' || role === 'technicien') && (
                <StatsCard title="Appareils" value={stats.total_appareils} color="blue" />
              )}
              {(role === 'patient' || role === 'medecin') && (
                <StatsCard title="Données" value={stats.total_donnees} color="green" />
              )}
              <StatsCard title="Alertes" value={stats.total_alertes} color="red" />
              {role === 'admin' && (
                <StatsCard title="Utilisateurs" value={stats.total_utilisateurs} color="yellow" />
              )}
            </div>
          </section>
        )}





        {/* Section Graphiques de santé */}
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg">
                <FontAwesomeIcon icon={faHeartPulse} className="text-white text-xl" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Données vitales (24h)</h2>
            </div>
            {donnees.length > 0 && (
              <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span>{donnees.length} mesures disponibles</span>
              </div>
            )}
          </div>
          
          {donnees.length === 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-6 group hover:shadow-xl transition-all duration-300">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                    <FontAwesomeIcon icon={faHeartPulse} className="text-red-500 dark:text-red-400 text-lg" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-800 dark:text-white">Fréquence cardiaque</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Mesures des dernières 24 heures</p>
                  </div>
                </div>
                <div className="h-64 flex items-center justify-center bg-slate-50 dark:bg-slate-900/50 rounded-lg border-2 border-dashed border-slate-300 dark:border-slate-600">
                  <div className="text-center">
                    <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-full w-16 h-16 mx-auto mb-3 flex items-center justify-center">
                      <FontAwesomeIcon icon={faHeartPulse} className="text-red-500 dark:text-red-400 text-2xl" />
                    </div>
                    <h4 className="font-medium text-slate-700 dark:text-slate-300 mb-1">Aucune donnée disponible</h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {role === 'medecin' 
                        ? "Les données des patients apparaîtront ici"
                        : "Connectez vos appareils de mesure"
                      }
                    </p>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Plage normale</span>
                    <span className="font-medium text-slate-700 dark:text-slate-300">60-100 BPM</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-6 group hover:shadow-xl transition-all duration-300">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                    <FontAwesomeIcon icon={faLungs} className="text-blue-500 dark:text-blue-400 text-lg" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-800 dark:text-white">Saturation en oxygène</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Mesures des dernières 24 heures</p>
                  </div>
                </div>
                <div className="h-64 flex items-center justify-center bg-slate-50 dark:bg-slate-900/50 rounded-lg border-2 border-dashed border-slate-300 dark:border-slate-600">
                  <div className="text-center">
                    <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full w-16 h-16 mx-auto mb-3 flex items-center justify-center">
                      <FontAwesomeIcon icon={faLungs} className="text-blue-500 dark:text-blue-400 text-2xl" />
                    </div>
                    <h4 className="font-medium text-slate-700 dark:text-slate-300 mb-1">Aucune donnée disponible</h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {role === 'medecin' 
                        ? "Les données des patients apparaîtront ici"
                        : "Connectez vos appareils de mesure"
                      }
                    </p>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Plage normale</span>
                    <span className="font-medium text-slate-700 dark:text-slate-300">≥95%</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-6 group hover:shadow-xl transition-all duration-300">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                    <FontAwesomeIcon icon={faHeartPulse} className="text-red-500 dark:text-red-400 text-lg" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-800 dark:text-white">Fréquence cardiaque</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Mesures des dernières 24 heures</p>
                  </div>
                </div>
                <div className="h-64">
                  <HealthChart
                    labels={donnees.map((d) => new Date(d.date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }))}
                    values={donnees.map((d) => d.frequence_cardiaque)}
                    label="BPM"
                    color="rgb(239,68,68)"
                  />
                </div>
                <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Plage normale</span>
                    <span className="font-medium text-slate-700 dark:text-slate-300">60-100 BPM</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-6 group hover:shadow-xl transition-all duration-300">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                    <FontAwesomeIcon icon={faLungs} className="text-blue-500 dark:text-blue-400 text-lg" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-slate-800 dark:text-white">Saturation en oxygène</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Mesures des dernières 24 heures</p>
                  </div>
                </div>
                <div className="h-64">
                  <HealthChart
                    labels={donnees.map((d) => new Date(d.date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }))}
                    values={donnees.map((d) => d.taux_oxygene)}
                    label="SpO₂ %"
                    color="rgb(59,130,246)"
                  />
                </div>
                <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Plage normale</span>
                    <span className="font-medium text-slate-700 dark:text-slate-300">≥95%</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Section Alertes */}
        <section className="space-y-6" id="alertes-section">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-red-500 to-orange-500 rounded-lg">
                <FontAwesomeIcon icon={faBell} className="text-white text-xl" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Alertes récentes</h2>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Surveillance en temps réel</span>
            </div>
          </div>
          
          {alertes.length === 0 ? (
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
              <div className="text-center py-12 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
                <div className="p-4 bg-green-100 dark:bg-green-900/50 rounded-full w-20 h-20 mx-auto mb-4 flex items-center justify-center">
                  <FontAwesomeIcon icon={faCheckCircle} className="text-3xl text-green-500 dark:text-green-400" />
                </div>
                <h3 className="text-lg font-semibold text-green-800 dark:text-green-200 mb-2">Aucune alerte active</h3>
                <p className="text-green-600 dark:text-green-300 max-w-md mx-auto mb-4">
                  {role === 'medecin' 
                    ? "Aucune alerte critique de vos patients. Système de surveillance actif."
                    : "Excellente nouvelle ! Toutes vos données de santé sont dans les paramètres normaux."
                  }
                </p>
                {role === 'medecin' && (
                  <div className="text-xs text-green-500 dark:text-green-400">
                    Les nouvelles alertes apparaîtront automatiquement ici
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
                  <thead className="bg-slate-50 dark:bg-slate-900">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">Niveau</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">Message</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                    {alertes.map((a) => (
                      <tr 
                        key={a.id} 
                        className={`transition-all duration-200 hover:bg-slate-50 dark:hover:bg-slate-700/50 group ${
                          a.user_id ? 'cursor-pointer' : 'cursor-default opacity-75'
                        }`} 
                        onClick={() => handleAlertClick(a)}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={
                              a.niveau === 'critique' || a.niveau === 'critical'
                                ? 'inline-flex items-center gap-2 px-3 py-2 rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-sm font-semibold border border-red-200 dark:border-red-800'
                                : a.niveau === 'modéré' || a.niveau === 'warning'
                                ? 'inline-flex items-center gap-2 px-3 py-2 rounded-full bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 text-sm font-semibold border border-orange-200 dark:border-orange-800'
                                : 'inline-flex items-center gap-2 px-3 py-2 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm font-semibold border border-blue-200 dark:border-blue-800'
                            }
                          >
                            {(a.niveau === 'critique' || a.niveau === 'critical') && (
                              <FontAwesomeIcon icon={faExclamationTriangle} className="text-red-500 dark:text-red-400" />
                            )}
                            {(a.niveau === 'modéré' || a.niveau === 'warning') && (
                              <FontAwesomeIcon icon={faExclamationTriangle} className="text-orange-500 dark:text-orange-400" />
                            )}
                            {a.niveau !== 'critique' && a.niveau !== 'critical' && a.niveau !== 'modéré' && a.niveau !== 'warning' && (
                              <FontAwesomeIcon icon={faBell} className="text-blue-500 dark:text-blue-400" />
                            )}
                            {a.niveau.charAt(0).toUpperCase() + a.niveau.slice(1)}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 font-medium">
                          {a.message}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400">
                          <div className="flex items-center gap-2">
                            <FontAwesomeIcon icon={faCalendarAlt} className="text-xs" />
                            {new Date(a.date).toLocaleString('fr-FR', {
                              day: '2-digit',
                              month: '2-digit',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>

        {/* Section Administration - Validation des médecins (Admin seulement) */}
        {role === 'admin' && (
          <section className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
                <FontAwesomeIcon icon={faStethoscope} className="text-white text-xl" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Gestion des médecins</h2>
            </div>
            <AdminApproval />
          </section>
        )}

        {/* Section Recommandations */}
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-green-500 to-teal-500 rounded-lg">
                <FontAwesomeIcon icon={faHeartPulse} className="text-white text-xl" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Recommandations personnalisées</h2>
            </div>
            <button
              onClick={refreshRecommandations}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <FontAwesomeIcon icon={faRefresh} className="text-sm" />
              Rafraîchir
            </button>
          </div>
          
          {loadingRecos ? (
            <div className="flex justify-center items-center p-12">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-blue-500 mx-auto mb-4"></div>
                <p className="text-slate-600 dark:text-slate-400">Chargement des recommandations...</p>
              </div>
            </div>
          ) : recoError ? (
            <div className="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-6">
              <div className="flex items-start gap-4">
                <div className="p-2 bg-yellow-100 dark:bg-yellow-900/50 rounded-lg">
                  <FontAwesomeIcon icon={faExclamationTriangle} className="text-yellow-600 dark:text-yellow-400 text-xl" />
                </div>
                <div>
                  <h3 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-1">Erreur de chargement</h3>
                  <p className="text-yellow-700 dark:text-yellow-300">{recoError}</p>
                </div>
              </div>
            </div>
          ) : recommandations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {recommandations.map((reco) => (
                <RecommendationCard 
                  key={reco.id} 
                  titre={reco.titre} 
                  description={reco.description} 
                  date={reco.date} 
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-800 dark:to-slate-700 rounded-xl border border-slate-200 dark:border-slate-600">
              <div className="p-4 bg-slate-100 dark:bg-slate-700 rounded-full w-20 h-20 mx-auto mb-4 flex items-center justify-center">
                <FontAwesomeIcon icon={faCheckCircle} className="text-3xl text-slate-400 dark:text-slate-500" />
              </div>
              <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-2">Aucune recommandation</h3>
              <p className="text-slate-600 dark:text-slate-400 max-w-md mx-auto">
                Vous n'avez pas encore de recommandations personnalisées. Elles apparaîtront automatiquement lorsque notre IA analysera vos données de santé.
              </p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
