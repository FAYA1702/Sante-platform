import { useEffect, useState } from 'react';
import api from '../api';
import StatsCard from '../components/StatsCard';
import RecommendationCard from '../components/RecommendationCard';
import HealthChart from '../components/HealthChart';
import Loader from '../components/Loader';

interface Alerte {
  id: string;
  message: string;
  niveau: string;
  date: string;
}

interface Recommendation {
  id: string;
  titre: string;
  description: string;
  date: string;
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

/**
 * Composant « Dashboard » : page d’accueil après connexion.
 * 
 * 1. Appelle l’API `/stats` pour afficher les cartes statistiques (appareils, données, utilisateurs…).
 * 2. Appelle l’API `/alerts` pour lister les alertes IA récentes.
 * 3. Appelle l’API `/data` pour récupérer les constantes vitales des dernières 24 heures et générer les graphiques.
 * 
 * Tous les appels sont effectués une seule fois à l’affichage initial grâce au `useEffect`.
 */
export default function Dashboard() {
  const [alertes, setAlertes] = useState<Alerte[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState('');
  const [donnees, setDonnees] = useState<DonneeSante[]>([]);
  const [recommandations, setRecommandations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  // Récupérer le nom utilisateur depuis le JWT ou localStorage (simple)
  let username = '';
  let role = '';
  try {
    const payload = JSON.parse(atob(localStorage.getItem('token')?.split('.')[1] || ''));
    username = payload.username || '';
    role = payload.role || '';
    if (!username) username = 'Utilisateur inconnu';
  } catch {}

  // Couleur d’accent selon le rôle
  const roleColor = role === 'admin' ? 'red' : role === 'medecin' ? 'green' : role === 'technicien' ? 'yellow' : 'blue';
  const roleLabel = role === 'admin' ? 'Administrateur' : role === 'medecin' ? 'Docteur' : role === 'technicien' ? 'Technicien' : 'Patient';

  useEffect(() => {
    (async () => {
      try {
        // --- Statistiques globales (cartes du haut) ---
        const { data } = await api.get('/stats');
        setStats(data);
      } catch (e) {
        console.error('Erreur stats', e);
      }
    })();
    (async () => {
      try {
        // --- Recommandations personnalisées ---
        const { data: recos } = await api.get('/recommendations').catch(() => ({ data: [] }));
        if (recos.length === 0) {
          // Recommandations fictives si l’API n’a rien renvoyé (démo)
          setRecommandations([
            { id: '1', titre: 'Hydratation', description: 'Buvez 1,5 L d’eau aujourd’hui pour maintenir une bonne hydratation.', date: new Date().toISOString() },
            { id: '2', titre: 'Activité physique', description: 'Effectuez 30 min de marche légère pour stimuler votre circulation.', date: new Date().toISOString() },
            { id: '3', titre: 'Sommeil', description: 'Essayez de dormir au moins 7 heures cette nuit pour favoriser la récupération.', date: new Date().toISOString() },
          ]);
        } else {
          setRecommandations(recos);
        }
        // --- Alertes récentes (tableau) ---
        const { data: alertesData } = await api.get('/alerts');
        setAlertes(alertesData);
        // données santé dernières 24h
        const fromIso = new Date(Date.now() - 24*60*60*1000).toISOString();
        const { data: donneesData } = await api.get(`/data?from=${fromIso}`);
        setDonnees(donneesData);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Erreur lors du chargement des données');
      } finally {
        setLoading(false);
      }
    })();
  }, []);



  if (loading) return <Loader />;

  return (
    <div className="relative p-5 space-y-6 min-h-screen bg-gradient-to-b from-blue-50 via-white to-white overflow-x-hidden">
      {/* Message d’accueil personnalisé avec avatar, rôle, bouton aide */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white/60 rounded-lg p-4 shadow mb-2">
        <div className="flex items-center gap-4">
          {/* Avatar profil */}
          <div className={`flex items-center justify-center w-14 h-14 rounded-full bg-${roleColor}-100 text-${roleColor}-700 text-2xl font-bold border-2 border-${roleColor}-300`}>
            {/* Icône avatar simple */}
            <svg width="32" height="32" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="8" r="4" />
              <path d="M5.5 21a7.5 7.5 0 0 1 13 0" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold mb-1">
              Bienvenue sur votre espace santé, <span className={`text-${roleColor}-700`}>{username}</span> !
              <span className={`ml-2 px-2 py-1 rounded text-xs font-semibold bg-${roleColor}-100 text-${roleColor}-700 align-middle`}>
                {roleLabel}
              </span>
            </h2>
            <p className="text-base text-slate-600">Accédez à vos appareils, vos données et vos recommandations personnalisées.</p>
          </div>
        </div>

      </div>

      {/* Gestion des erreurs UX */}
      {error && (
        <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 rounded p-3 mb-3">
          <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" className="fill-red-100"/>
            <path d="M12 8v4m0 4h.01" strokeLinecap="round"/>
          </svg>
          <span>{error}</span>
        </div>
      )}

      {/*
        Affichage conditionnel des cartes statistiques selon le rôle utilisateur.
        - Appareils : visible pour admin et technicien
        - Données : visible pour patient et medecin
        - Utilisateurs : visible uniquement pour admin
        - Alertes : visible pour tous
      */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
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
      )}
      <section className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Alertes récentes</h2>
        {error && <p className="text-red-500 mb-2">{error}</p>}
        {alertes.length === 0 ? (
          <p>Aucune alerte.</p>
        ) : (
          <div className="overflow-x-auto bg-white rounded-lg shadow">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Niveau</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Message</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {alertes.map((a) => (
                  <tr key={a.id} className="transition hover:bg-blue-50/60 hover:shadow rounded-lg">                    {/* Badge coloré selon le niveau d’alerte (critique, modéré, info) */}
                    <td className="px-6 py-4 whitespace-nowrap font-semibold">
                      <span
                          className={
                            a.niveau === 'critique'
                              ? 'inline-flex items-center gap-1 px-2 py-1 rounded bg-red-100 text-red-700 text-xs font-bold shadow-sm'
                              : a.niveau === 'modéré'
                              ? 'inline-flex items-center gap-1 px-2 py-1 rounded bg-orange-100 text-orange-700 text-xs font-bold shadow-sm'
                              : 'inline-flex items-center gap-1 px-2 py-1 rounded bg-blue-100 text-blue-700 text-xs font-bold shadow-sm'
                          }
                          title={
                            a.niveau === 'critique'
                              ? 'Alerte critique : nécessite une intervention immédiate.'
                              : a.niveau === 'modéré'
                              ? 'Alerte modérée : surveiller la situation.'
                              : 'Information : pas d’action urgente.'
                          }
                        >
                          {/* Icône selon le niveau */}
                          {a.niveau === 'critique' && (
                            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                              <circle cx="12" cy="12" r="10" className="fill-red-200"/>
                              <path d="M12 8v4m0 4h.01" strokeLinecap="round"/>
                            </svg>
                          )}
                          {a.niveau === 'modéré' && (
                            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                              <circle cx="12" cy="12" r="10" className="fill-orange-200"/>
                              <path d="M12 8v4m0 4h.01" strokeLinecap="round"/>
                            </svg>
                          )}
                          {a.niveau !== 'critique' && a.niveau !== 'modéré' && (
                            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                              <circle cx="12" cy="12" r="10" className="fill-blue-200"/>
                              <path d="M12 16h.01" strokeLinecap="round"/>
                            </svg>
                          )}
                          {a.niveau.charAt(0).toUpperCase() + a.niveau.slice(1)}
                        </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">{a.message}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{new Date(a.date).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      {/* Graphiques santé */}
      {donnees.length > 0 && (
        <section className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold mb-2">Fréquence cardiaque (24h)</h3>
            {/*
                Graphique de la fréquence cardiaque (rouge médical, courbe lissée)
                - labels : heures des mesures
                - values : fréquence cardiaque (BPM)
                - color : rouge vif Tailwind
              */}
              <HealthChart
                labels={donnees.map((d) => new Date(d.date).toLocaleTimeString())}
                values={donnees.map((d) => d.frequence_cardiaque)}
                label="BPM"
                color="rgb(220,38,38)" // rouge médical
              />
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold mb-2">Taux d'oxygène (24h)</h3>
            {/*
                Graphique du taux d’oxygène (bleu médical, courbe lissée)
                - labels : heures des mesures
                - values : SpO₂ (%)
                - color : bleu médical
              */}
              <HealthChart
                labels={donnees.map((d) => new Date(d.date).toLocaleTimeString())}
                values={donnees.map((d) => d.taux_oxygene)}
                label="SpO₂ %"
                color="rgb(37,99,235)" // bleu médical
              />
          </div>
        </section>
      )}
      {/* Recommandations personnalisées */}
      {recommandations.length > 0 && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Recommandations personnalisées</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommandations.map((r) => (
              <RecommendationCard key={r.id} titre={r.titre} description={r.description} date={r.date} />
            ))}
          </div>
        </section>
      )}
      {/* Illustration médicale en fond bas de page */}
      <svg className="absolute bottom-0 left-0 w-full h-48 opacity-20 pointer-events-none select-none" viewBox="0 0 1440 320">
        <defs>
          <linearGradient id="fondMed" x1="0" x2="0" y1="0" y2="1">
            <stop stopColor="#38bdf8" stopOpacity="0.12" />
            <stop offset="1" stopColor="#a7f3d0" stopOpacity="0.10" />
          </linearGradient>
        </defs>
        <path fill="url(#fondMed)" d="M0,128L80,144C160,160,320,192,480,202.7C640,213,800,203,960,202.7C1120,203,1280,213,1360,218.7L1440,224L1440,320L1360,320C1280,320,1120,320,960,320C800,320,640,320,480,320C320,320,160,320,80,320L0,320Z"></path>
      </svg>
    </div>
  );
}
