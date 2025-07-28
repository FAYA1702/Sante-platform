import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Loader from '../components/Loader';

/**
 * Page Appareils (protégée RBAC frontend)
 * Seuls les administrateurs et techniciens peuvent accéder à cette page.
 */
export default function Devices() {
  const navigate = useNavigate();
  let role = '';
  try {
    const payload = JSON.parse(atob(localStorage.getItem('token')?.split('.')[1] || ''));
    role = payload.role || '';
  } catch {}

  const [showAlert, setShowAlert] = useState(false);
  useEffect(() => {
    if (role !== 'admin' && role !== 'technicien') {
      setShowAlert(true);
      setTimeout(() => {
        setShowAlert(false);
        navigate('/');
      }, 2000);
    }
  }, [role, navigate]);

  if (role !== 'admin' && role !== 'technicien') return (
    <>
      {showAlert && (
        <div style={{position: 'fixed', top: 24, left: '50%', transform: 'translateX(-50%)', zIndex: 50}}>
          <div className="bg-red-100 border border-red-300 text-red-800 px-6 py-3 rounded shadow-lg flex items-center gap-3 animate-fade-in">
            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" className="fill-red-200" />
              <path d="M12 8v4m0 4h.01" strokeLinecap="round" />
            </svg>
            <span className="font-semibold">Accès refusé : seuls les administrateurs et techniciens peuvent accéder à la gestion des appareils.</span>
          </div>
        </div>
      )}
      <Loader />
    </>
  );

  const [appareils, setAppareils] = useState<any[]>([]);
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Types d'appareils standardisés
  const typesAppareils = [
    "Oxymètre",
    "Tensiomètre",
    "ECG",
    "Thermomètre",
    "Glucomètre",
    "Bracelet d'activité",
    "Balance connectée",
    "Spiromètre"
  ];

  // Formulaire de création d'appareil
  const [form, setForm] = useState({
    type: '',
    numero_serie: '',
    user_id: ''
  });

  // Chargement des appareils
  useEffect(() => {
    setLoading(true);
    setError(null);
    import('../api').then(({ default: api }) => {
      api.get('/devices')
        .then(res => {
          setAppareils(res.data);
          setLoading(false);
        })
        .catch(err => {
          console.error('Erreur chargement appareils:', err);
          setError('Erreur lors du chargement des appareils.');
          setLoading(false);
        });
    });
  }, []);

  // Chargement des patients (pour le sélecteur)
  useEffect(() => {
    import('../api').then(({ default: api }) => {
      api.get('/users/patients')
        .then(res => {
          setPatients(res.data);
        })
        .catch(err => {
          console.error('Erreur chargement patients:', err);
          setError('Erreur lors du chargement des patients.');
        });
    });
  }, []);

  // Gestion du formulaire
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  // Soumission du formulaire
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    import('../api').then(({ default: api }) => {
      api.post('/devices', form)
        .then(res => {
          setAppareils([...appareils, res.data]);
          setForm({ type: '', numero_serie: '', user_id: '' });
          setSuccess('Appareil créé avec succès.');
          setLoading(false);
          
          // Masquer le message de succès après 3 secondes
          setTimeout(() => setSuccess(null), 3000);
        })
        .catch(err => {
          console.error('Erreur création appareil:', err);
          setError('Erreur lors de la création de l\'appareil.');
          setLoading(false);
        });
    });
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Gestion des appareils</h1>
      
      {/* Messages d'erreur/succès */}
      {error && (
        <div className="bg-red-100 border border-red-300 text-red-800 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-100 border border-green-300 text-green-800 px-4 py-3 rounded mb-4">
          {success}
        </div>
      )}

      {/* Formulaire de création */}
      <div className="bg-gray-50 border rounded p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">Ajouter un appareil</h2>
        <form onSubmit={handleSubmit} className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold mb-1">Type d'appareil</label>
            <select
              name="type"
              required
              value={form.type}
              onChange={handleChange}
              className="border px-2 py-1 rounded w-60"
            >
              <option value="" disabled>Sélectionner un type</option>
              {typesAppareils.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1">Numéro de série</label>
            <input 
              name="numero_serie" 
              type="text" 
              required 
              value={form.numero_serie} 
              onChange={handleChange} 
              className="border px-2 py-1 rounded w-40" 
              placeholder="SN12345"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1">Patient propriétaire</label>
            <select 
              name="user_id" 
              required 
              value={form.user_id} 
              onChange={handleChange} 
              className="border px-2 py-1 rounded w-60">
              <option value="" disabled>Sélectionner un patient</option>
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.username} ({patient.email})
                </option>
              ))}
            </select>
          </div>
          <div>
            <button 
              type="submit" 
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1 rounded"
              disabled={loading}
            >
              {loading ? 'Chargement...' : 'Ajouter'}
            </button>
          </div>
        </form>
      </div>

      {/* Liste des appareils */}
      <h2 className="text-lg font-semibold mb-3">Appareils enregistrés</h2>
      {loading && <Loader />}
      
      {!loading && appareils.length === 0 && (
        <p className="text-gray-500 italic">Aucun appareil enregistré.</p>
      )}
      
      {appareils.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border">
            <thead>
              <tr className="bg-gray-100 text-gray-700">
                <th className="py-2 px-4 border text-left">#</th>
                <th className="py-2 px-4 border text-left">Type</th>
                <th className="py-2 px-4 border text-left">Numéro de série</th>
                <th className="py-2 px-4 border text-left">Patient</th>
              </tr>
            </thead>
            <tbody>
              {appareils.map((appareil, index) => (
                <tr key={appareil.id} className="hover:bg-gray-50">
                  <td className="py-2 px-4 border text-center font-semibold">
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full" title={appareil.id}>
                      {index + 1}
                    </span>
                  </td>
                  <td className="py-2 px-4 border">{appareil.type}</td>
                  <td className="py-2 px-4 border">{appareil.numero_serie}</td>
                  <td className="py-2 px-4 border">
                    {appareil.user_id ? 
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                        Patient #{appareil.user_id.substring(0, 4)}
                      </span> : 
                      <span className="text-gray-400 italic">Non assigné</span>
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
