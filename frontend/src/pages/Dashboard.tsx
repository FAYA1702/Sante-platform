import { useEffect, useState } from 'react';
import api from '../api';
import StatsCard from '../components/StatsCard';
import HealthChart from '../components/HealthChart';

interface Alerte {
  id: string;
  message: string;
  niveau: string;
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
        // --- Alertes récentes (tableau) ---
        const { data: alertesData } = await api.get('/alerts');
        setAlertes(alertesData);
        // données santé dernières 24h
        const fromIso = new Date(Date.now() - 24*60*60*1000).toISOString();
        const { data: donneesData } = await api.get(`/data?from=${fromIso}`);
        setDonnees(donneesData);

      } catch (err: any) {
        setError(err.response?.data?.detail || 'Erreur lors du chargement des alertes');
      }
    })();
  }, []);



  return (
    <div className="p-5 space-y-6">
      <h1 className="text-3xl font-bold mb-6">Tableau de bord</h1>

      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard title="Appareils" value={stats.total_appareils} color="blue" />
          <StatsCard title="Données" value={stats.total_donnees} color="green" />
          <StatsCard title="Alertes" value={stats.total_alertes} color="red" />
          <StatsCard title="Utilisateurs" value={stats.total_utilisateurs} color="yellow" />
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
                  <tr key={a.id} className="hover:bg-slate-50">
                    {/* Badge coloré selon le niveau d’alerte (critique, modéré, info) */}
                    <td className="px-6 py-4 whitespace-nowrap font-semibold">
                      <span
                        className={
                          a.niveau === 'critique'
                            ? 'inline-block px-2 py-1 rounded bg-red-100 text-red-700 text-xs font-bold'
                            : a.niveau === 'modéré'
                            ? 'inline-block px-2 py-1 rounded bg-orange-100 text-orange-700 text-xs font-bold'
                            : 'inline-block px-2 py-1 rounded bg-blue-100 text-blue-700 text-xs font-bold'
                        }
                      >
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
    </div>
  );
}
