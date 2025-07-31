import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api';
import Loader from '../components/Loader';

interface PatientSummary {
  id: string;
  nom: string;
  email: string;
  last_data: any;
}

interface PatientHistory {
  donnees: any[];
  alertes: any[];
  recommandations: any[];
}

export default function PatientPage() {
  const { id } = useParams<{ id: string }>();
  const [summary, setSummary] = useState<PatientSummary | null>(null);
  const [history, setHistory] = useState<PatientHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;

    (async () => {
      try {
        setLoading(true);
        const [summaryRes, historyRes] = await Promise.all([
          api.get(`/patients/${id}/summary`),
          api.get(`/patients/${id}/history`)
        ]);
        setSummary(summaryRes.data);
        setHistory(historyRes.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Erreur lors du chargement');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);



  if (loading) return <Loader />;
  if (error) return <div className="text-red-500 p-4">{error}</div>;
  if (!summary) return <div className="p-4">Patient introuvable</div>;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Breadcrumb */}
      <nav className="mb-6">
        <Link to="/" className="text-blue-600 hover:underline">Tableau de bord</Link>
        <span className="mx-2 text-gray-500">›</span>
        <span className="text-gray-700">Fiche patient</span>
      </nav>

      {/* En-tête patient */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
            <svg width="32" height="32" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" className="text-blue-600">
              <circle cx="12" cy="8" r="4" />
              <path d="M5.5 21a7.5 7.5 0 0 1 13 0" />
            </svg>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{summary.nom}</h1>
            <p className="text-gray-600">{summary.email}</p>
            <p className="text-sm text-gray-500">ID: {summary.id}</p>
          </div>
        </div>

        {/* Dernières données */}
        {summary.last_data && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold mb-2">Dernières mesures</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Fréquence cardiaque:</span>
                <span className="ml-2 font-medium">{summary.last_data.frequence_cardiaque || 'N/A'} bpm</span>
              </div>
              <div>
                <span className="text-gray-600">SpO2:</span>
                <span className="ml-2 font-medium">{summary.last_data.taux_oxygene || 'N/A'}%</span>
              </div>
              <div>
                <span className="text-gray-600">Date:</span>
                <span className="ml-2 font-medium">{new Date(summary.last_data.date).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Onglets historique */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alertes */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold flex items-center">
              <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" className="mr-2 text-red-500">
                <path d="M15 17h5l-1.405-1.405C18.79 14.79 18 13.42 18 12V8c0-3.314-2.686-6-6-6S6 4.686 6 8v4c0 1.42-.79 2.79-1.595 3.595L3 17h5m4 4h0" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Alertes ({history?.alertes.length || 0})
            </h2>
          </div>
          <div className="p-4 max-h-96 overflow-y-auto">
            {history?.alertes.length ? (
              <div className="space-y-3">
                {history.alertes.map((alerte, idx) => (
                  <div key={idx} className="p-3 border rounded-lg">
                    <div className={`inline-block px-2 py-1 rounded text-xs font-medium mb-2 ${
                      alerte.niveau === 'élevé' ? 'bg-red-100 text-red-800' :
                      alerte.niveau === 'moyen' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {alerte.niveau}
                    </div>
                    <p className="text-sm text-gray-700">{alerte.message}</p>
                    <p className="text-xs text-gray-500 mt-1">{new Date(alerte.date).toLocaleString()}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">Aucune alerte</p>
            )}
          </div>
        </div>

        {/* Données santé */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold flex items-center">
              <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" className="mr-2 text-green-500">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Données ({history?.donnees.length || 0})
            </h2>
          </div>
          <div className="p-4 max-h-96 overflow-y-auto">
            {history?.donnees.length ? (
              <div className="space-y-3">
                {history.donnees.slice(0, 10).map((donnee, idx) => (
                  <div key={idx} className="p-3 border rounded-lg">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm"><strong>FC:</strong> {donnee.frequence_cardiaque} bpm</p>
                        <p className="text-sm"><strong>SpO2:</strong> {donnee.taux_oxygene}%</p>
                      </div>
                      <span className="text-xs text-gray-500">{new Date(donnee.date).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">Aucune donnée</p>
            )}
          </div>
        </div>

        {/* Recommandations */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold flex items-center">
                <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" className="mr-2 text-purple-500">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Recommandations IA ({history?.recommandations.length || 0})
              </h2>
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                Générées automatiquement
              </span>
            </div>
          </div>
          <div className="p-4 max-h-96 overflow-y-auto">
            {history?.recommandations.length ? (
              <div className="space-y-3">
                {history.recommandations.map((reco, idx) => (
                  <div key={idx} className="p-3 border rounded-lg">
                    <h4 className="font-medium text-sm">{reco.titre}</h4>
                    <p className="text-sm text-gray-700 mt-1">{reco.description}</p>
                    <p className="text-xs text-gray-500 mt-2">{new Date(reco.date).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">Aucune recommandation</p>
            )}
          </div>
        </div>
      </div>


    </div>
  );
}
