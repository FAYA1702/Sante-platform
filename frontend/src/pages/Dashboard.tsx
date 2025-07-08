import { useEffect, useState } from 'react';
import api from '../api';

interface Alerte {
  id: string;
  message: string;
  niveau: string;
  date: string;
}

export default function Dashboard() {
  const [alertes, setAlertes] = useState<Alerte[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get('/alerts');
        setAlertes(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Erreur lors du chargement des alertes');
      }
    })();
  }, []);

  const logout = () => {
    localStorage.removeItem('token');
    window.location.href = '/auth';
  };

  return (
    <div style={{ padding: 20 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Tableau de bord</h1>
        <button onClick={logout}>Se déconnecter</button>
      </header>
      <section>
        <h2>Alertes récentes</h2>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {alertes.length === 0 && <p>Aucune alerte.</p>}
        <ul>
          {alertes.map((a) => (
            <li key={a.id} style={{ marginBottom: 10 }}>
              <strong>{a.niveau}</strong> – {a.message} ({new Date(a.date).toLocaleString()})
            </li>
          ))}
        </ul>
      </section>
      {/* Placeholder pour les graphiques de données santé */}
      <section>
        <h2>Graphiques santé (bientôt)</h2>
        <p>Les visualisations de la fréquence cardiaque et SpO₂ arriveront dans la prochaine itération.</p>
      </section>
    </div>
  );
}
