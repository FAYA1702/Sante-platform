import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Loader from '../components/Loader';

// Utilitaire export CSV
function exportCsv(filename: string, rows: string[][]) {
  const csvContent = rows.map(r => r.map(v => `"${v.replace(/"/g, '""')}"`).join(',')).join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Seuils cohérents avec le micro-service IA
const FC_MAX = Number(import.meta.env.VITE_FC_MAX ?? 100);
const SPO2_MIN = Number(import.meta.env.VITE_SPO2_MIN ?? 92);

/**
 * Page Données santé (protégée RBAC frontend)
 * Seuls les patients et médecins peuvent accéder à cette page.
 * Option démo : l'admin peut accéder pour démonstration (voir commentaire RGPD dans le code).
 */
export default function Data() {
  const navigate = useNavigate();
  let role = '';
  try {
    const payload = JSON.parse(atob(localStorage.getItem('token')?.split('.')[1] || ''));
    role = payload.role || '';
  } catch {}

  const [showAlert, setShowAlert] = useState(false);
  useEffect(() => {
    // Option démo : autoriser admin à accéder (sinon retirer 'role === "admin"')
    if (role !== 'patient' && role !== 'medecin' && role !== 'admin') {
      setShowAlert(true);
      setTimeout(() => {
        setShowAlert(false);
        navigate('/');
      }, 2000);
    }
  }, [role, navigate]);

  if (role !== 'patient' && role !== 'medecin' && role !== 'admin') return (
    <>
      {showAlert && (
        <div style={{position: 'fixed', top: 24, left: '50%', transform: 'translateX(-50%)', zIndex: 50}}>
          <div className="bg-red-100 border border-red-300 text-red-800 px-6 py-3 rounded shadow-lg flex items-center gap-3 animate-fade-in">
            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" className="fill-red-200" />
              <path d="M12 8v4m0 4h.01" strokeLinecap="round" />
            </svg>
            <span className="font-semibold">Accès refusé : seuls les patients et médecins peuvent accéder aux données santé.</span>
          </div>
        </div>
      )}
      <Loader />
    </>
  );

  const [donnees, setDonnees] = useState<any[]>([]);
  const [devices, setDevices] = useState<any[]>([]);
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (role === 'patient' || role === 'medecin' || role === 'admin') {
      setLoading(true);
      setError(null);
      import('../api').then(({ default: api }) => {
        api.get('/data')
          .then(res => setDonnees(res.data))
          .catch(e => setError('Erreur lors du chargement des données santé.'))
          .finally(() => setLoading(false));
      });
    }
  }, [role]);

  // Charge les appareils du patient (liste déroulante)
  useEffect(() => {
    if (role === 'patient') {
      import('../api').then(({ default: api }) => {
        api.get('/my/devices')
          .then(res => {
            setDevices(res.data);
            if (res.data.length === 1) {
              setForm(prev => ({ ...prev, device_id: res.data[0].id }));
            }
          })
          .catch(() => setError('Erreur lors du chargement des appareils.'));
      });
    }
  }, [role]);

  // Charge la liste des patients pour le filtre médecin
  useEffect(() => {
    if (role === 'medecin') {
      import('../api').then(({ default: api }) => {
        api.get('/users/patients')
          .then(res => setPatients(res.data))
          .catch(() => console.error('Erreur lors du chargement des patients'));
      });
    } else {
      setPatients([]);
    }
  }, [role]);

  // --- Formulaire d’ajout de donnée santé ---
  const [form, setForm] = useState({
    device_id: '',
    frequence_cardiaque: '',
    pression_arterielle: '',
    taux_oxygene: '',
    date: new Date().toISOString().slice(0, 16), // format local pour input type datetime-local
  });
  const [sending, setSending] = useState(false);
  const [success, setSuccess] = useState<string|null>(null);

  // Filtres et pagination
  const [filters, setFilters] = useState({ patient: '', start: '', end: '' });
  const [page, setPage] = useState(1);
  const itemsPerPage = 10;
  const [formError, setFormError] = useState<string|null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);
    setFormError(null);
    setSuccess(null);
    import('../api').then(({ default: api }) => {
      api.post('/data', {
        device_id: form.device_id,
        frequence_cardiaque: form.frequence_cardiaque ? parseFloat(form.frequence_cardiaque) : undefined,
        pression_arterielle: form.pression_arterielle || undefined,
        taux_oxygene: form.taux_oxygene ? parseFloat(form.taux_oxygene) : undefined,
        date: new Date(form.date).toISOString(),
      })
        .then(() => {
          setSuccess('Donnée ajoutée avec succès !');
          setForm({ ...form, frequence_cardiaque: '', pression_arterielle: '', taux_oxygene: '', date: new Date().toISOString().slice(0, 16) });
          // Recharge la liste
          setLoading(true);
          import('../api').then(({ default: api }) => {
            api.get('/data')
              .then(res => setDonnees(res.data))
              .catch(e => setError('Erreur lors du chargement des données santé.'))
              .finally(() => setLoading(false));
          });
        })
        .catch(() => setFormError('Erreur lors de l’ajout de la donnée.'))
        .finally(() => setSending(false));
    });
  };

  // Associe le nom patient s’il manque, à partir de la liste patients
  const usernameMap = Object.fromEntries(patients.map((p:any)=>[p.id, p.username]));
  const donneesEnrichies = donnees.map((d:any)=> ({...d, patient_nom: d.patient_nom ?? usernameMap[d.user_id]}));

  // Applique filtres date/patient
  const filteredDonnees = donneesEnrichies.filter((d:any) => {
    const okPatient = filters.patient ? ((d.patient_nom ?? '').toLowerCase().includes(filters.patient.toLowerCase())) : true;
    const okStart = filters.start ? new Date(d.date) >= new Date(filters.start) : true;
    const okEnd = filters.end ? new Date(d.date) <= new Date(filters.end) : true;
    return okPatient && okStart && okEnd;
  });
  const totalPages = Math.ceil(filteredDonnees.length / itemsPerPage) || 1;
  const paginated = filteredDonnees.slice((page - 1) * itemsPerPage, page * itemsPerPage);

  const handleExportCsv = () => {
    const rows = [
      ['Date', 'Appareil', 'Fréquence cardiaque', 'Pression artérielle', 'Taux O₂', 'Provenance'],
      ...filteredDonnees.map((d:any) => [
        new Date(d.date).toLocaleString(),
        d.device_id,
        String(d.frequence_cardiaque ?? ''),
        d.pression_arterielle ?? '',
        String(d.taux_oxygene ?? ''),
        d.source ?? '',
      ]),
    ];
    exportCsv('donnees_sante.csv', rows);
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Données santé</h1>
        {filteredDonnees.length > 0 && (
          <button onClick={handleExportCsv} className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 text-sm">Exporter CSV</button>
        )}
      </div>
      {/* Mention RGPD / finalité médicale */}
<p className="text-xs text-slate-500 mb-2">
  Ces données de santé sont traitées uniquement à des fins de suivi médical. Conformément au RGPD, elles ne
  seront jamais utilisées à d’autres fins sans consentement explicite.
</p>
{role === 'admin' && (
  <p className="text-xs text-orange-600 mb-2">
    (Accès admin activé pour la démo, à désactiver en production)
  </p>
)}
      {role === 'medecin' && (
        <div className="mb-4 flex flex-wrap gap-4 items-end bg-gray-50 border rounded p-4">
          <div>
            <label className="block text-xs font-semibold mb-1">Patient</label>
            {patients.length > 0 ? (
              <select value={filters.patient} onChange={e=>{setFilters({...filters, patient:e.target.value}); setPage(1);}} className="border px-2 py-1 rounded w-56">
                <option value="">Tous</option>
                {patients.map((p:any) => (
                  <option key={p.id} value={p.username}>{p.username}</option>
                ))}
              </select>
            ) : (
              <input type="text" value={filters.patient} onChange={e=>{setFilters({...filters, patient:e.target.value}); setPage(1);}} className="border px-2 py-1 rounded w-56" placeholder="Nom patient" />
            )}
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1">Du</label>
            <input type="date" value={filters.start} onChange={e=>{setFilters({...filters, start:e.target.value}); setPage(1);}} className="border px-2 py-1 rounded" />
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1">Au</label>
            <input type="date" value={filters.end} onChange={e=>{setFilters({...filters, end:e.target.value}); setPage(1);}} className="border px-2 py-1 rounded" />
          </div>
        </div>
      )}
      {(role === 'patient' || role === 'medecin' || role === 'admin') && (
        <form onSubmit={handleSubmit} className="mb-6 bg-gray-50 border rounded p-4 flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold mb-1">Appareil</label>
            {role === 'patient' ? (
              devices.length > 0 ? (
                <select name="device_id" required value={form.device_id} onChange={e => setForm({ ...form, device_id: e.target.value })} className="border px-2 py-1 rounded w-40">
                  <option value="" disabled>Sélectionner</option>
                  {devices.map((d:any) => (
                    <option key={d.id} value={d.id}>{d.type} · {d.numero_serie}</option>
                  ))}
                </select>
              ) : (
                <span className="text-red-600 text-sm">Aucun appareil enregistré</span>
              )
            ) : (
              <input name="device_id" type="text" required value={form.device_id} onChange={handleChange} className="border px-2 py-1 rounded w-32" />
            )}
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1">Fréquence cardiaque (bpm)</label>
            <input name="frequence_cardiaque" type="number" min="0" value={form.frequence_cardiaque} onChange={handleChange} className="border px-2 py-1 rounded w-32" />
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1">Pression artérielle</label>
            <input name="pression_arterielle" type="text" placeholder="120/80" value={form.pression_arterielle} onChange={handleChange} className="border px-2 py-1 rounded w-24" />
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1">Taux O₂ (%)</label>
            <input name="taux_oxygene" type="number" min="0" max="100" value={form.taux_oxygene} onChange={handleChange} className="border px-2 py-1 rounded w-20" />
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1">Date</label>
            <input name="date" type="datetime-local" required value={form.date} onChange={handleChange} className="border px-2 py-1 rounded w-52" />
          </div>
          <button type="submit" disabled={sending} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50">{sending ? 'Ajout...' : 'Ajouter'}</button>
          {formError && <div className="text-red-700 ml-2">{formError}</div>}
          {success && <div className="text-green-700 ml-2">{success}</div>}
        </form>
      )}
      {loading ? <Loader /> : error ? (
        <div className="bg-red-100 border border-red-300 text-red-800 px-4 py-2 rounded mb-4">{error}</div>
      ) : donnees.length === 0 ? (
        <div className="text-gray-500">Aucune donnée de santé trouvée.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full border mt-4">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-2">Date</th>
                <th className="px-4 py-2">Appareil</th>
                <th className="px-4 py-2">Fréquence cardiaque</th>
                <th className="px-4 py-2">Pression artérielle</th>
                <th className="px-4 py-2">Taux O₂</th>
                <th className="px-4 py-2">Provenance</th>
              </tr>
            </thead>
            <tbody>
              {paginated.map((d, i) => (
                <tr key={d.id || i} className="border-b">
                  <td className="px-4 py-2">{new Date(d.date).toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">{d.device_nom || d.device_id}</td>
                  <td className={d.frequence_cardiaque > FC_MAX ? 'text-red-600 font-semibold' : ''}>{d.frequence_cardiaque}</td>
                  <td className="px-4 py-2">{d.pression_arterielle ?? '-'}</td>
                  <td className={d.taux_oxygene < SPO2_MIN ? 'text-red-600 font-semibold' : ''}>{d.taux_oxygene}</td>
                  <td className="px-4 py-2">{d.source ?? '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-2 flex gap-2 items-center">
              <button disabled={page===1} onClick={()=>setPage(p=>p-1)} className="px-2 py-1 border rounded disabled:opacity-40">Préc.</button>
              <span className="text-sm">Page {page}/{totalPages}</span>
              <button disabled={page===totalPages} onClick={()=>setPage(p=>p+1)} className="px-2 py-1 border rounded disabled:opacity-40">Suiv.</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
