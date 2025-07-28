
/**
 * Comment utiliser / tester la protection RBAC frontend sur /users :
 * 1. Connecte-toi avec un compte non-admin (patient, technicien, médecin).
 * 2. Essaie d’accéder à /users via l’URL (barre d’adresse ou lien direct).
 * 3. Tu verras une alerte « Accès refusé » et tu seras immédiatement redirigé vers le dashboard.
 *
 * Cette protection empêche tout utilisateur non autorisé de consulter ou manipuler la gestion des utilisateurs,
 * même en cas de tentative d’accès direct par l’URL.
 */
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import Loader from '../components/Loader';

/**
 * Page Gestion utilisateurs (protégée RBAC frontend)
 * Seul un administrateur peut accéder à cette page.
 */
export default function Users() {
  const navigate = useNavigate();
  let role = '';
  try {
    const payload = JSON.parse(atob(localStorage.getItem('token')?.split('.')[1] || ''));
    role = payload.role || '';
  } catch {}

  const [showAlert, setShowAlert] = useState(false);
  useEffect(() => {
    if (role !== 'admin') {
      setShowAlert(true);
      setTimeout(() => {
        setShowAlert(false);
        navigate('/');
      }, 2000); // Affiche l’alerte 2s puis redirige
    }
  }, [role, navigate]);

  if (role !== 'admin') return (
    <>
      {showAlert && (
        <div style={{position: 'fixed', top: 24, left: '50%', transform: 'translateX(-50%)', zIndex: 50}}>
          <div className="bg-red-100 border border-red-300 text-red-800 px-6 py-3 rounded shadow-lg flex items-center gap-3 animate-fade-in">
            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" className="fill-red-200" />
              <path d="M12 8v4m0 4h.01" strokeLinecap="round" />
            </svg>
            <span className="font-semibold">Accès refusé : seuls les administrateurs peuvent accéder à la gestion des utilisateurs.</span>
          </div>
        </div>
      )}
      <Loader />
    </>
  );

  const [users, setUsers] = useState<Array<{ id: string; email: string; username: string; role: string }>>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selected, setSelected] = useState<{ id?: string; email: string; username: string; role: string } | null>(null);
  const [form, setForm] = useState({ email: '', username: '', role: 'patient', mot_de_passe: '' });
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const pageSize = 20;
  const [hasMore, setHasMore] = useState(true);

  // Helper to color badges per rôle
  const roleColors: Record<string, string> = {
    patient: 'bg-blue-100 text-blue-800',
    medecin: 'bg-green-100 text-green-800',
    technicien: 'bg-purple-100 text-purple-800',
    admin: 'bg-red-100 text-red-800',
  };

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params: any = { skip: page * pageSize, limit: pageSize };
      if (search.trim()) params.q = search.trim();
      const res = await api.get('/users', { params });
      setUsers(res.data);
      setHasMore(res.data.length === pageSize);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [page, search]);

  const handleEdit = (u: { id: string; email: string; username: string; role: string }) => {
    setSelected(u);
    setForm({ email: u.email, username: u.username, role: u.role, mot_de_passe: '' });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Confirmer la suppression de cet utilisateur ?')) return;
    try {
      await api.delete(`/users/${id}`);
      setUsers((u) => u.filter((x) => x.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Erreur de suppression');
    }
  };

  if (loading) return <Loader />;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Gestion des utilisateurs</h1>
        <div className="relative ml-4">
          <svg
            className="absolute left-2 top-1.5 h-4 w-4 text-slate-400 pointer-events-none"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M21 21l-4.35-4.35m1.38-4.63a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            type="text"
            placeholder="Recherche email/username…"
            value={search}
            onChange={(e) => {
              setPage(0);
              setSearch(e.target.value);
            }}
            className="pl-8 border px-2 py-1 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          className="px-3 py-1 rounded bg-blue-600 hover:bg-blue-700 text-white"
          onClick={() => {
            setSelected(null);
            setShowModal(true);
          }}
        >
          + Ajouter
        </button>
      </div>
      {error && <p className="text-red-600 mb-4">{error}</p>}
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white shadow rounded">
          <thead className="sticky top-0 bg-white shadow-sm">
            <tr>
              <th className="text-left p-2">Email</th>
              <th className="text-left p-2">Username</th>
              <th className="text-left p-2">Rôle</th>
              <th className="text-right p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u, idx) => (
              <tr key={u.id} className={idx % 2 ? 'odd:bg-slate-50' : ''}>
                <td className="p-2">{u.email}</td>
                <td className="p-2">{u.username}</td>
                <td className="p-2">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${roleColors[u.role]}`}>{u.role}</span>
                </td>
                <td className="p-2 text-right space-x-2">
                  <button
                    onClick={() => handleEdit(u)}
                    title="Modifier"
                    className="px-2 py-1 text-sm bg-amber-500 hover:bg-amber-600 text-white rounded inline-flex items-center gap-1 transform hover:scale-105 transition-transform"
                  >
                    ✏️ <span className="sr-only">Modifier</span>
                  </button>
                  <button
                    onClick={() => handleDelete(u.id)}
                    title="Supprimer"
                    className="px-2 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded inline-flex items-center gap-1 transform hover:scale-105 transition-transform"
                  >
                    🗑️ <span className="sr-only">Supprimer</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-center items-center gap-4 mt-4">
        <button
          disabled={page === 0}
          onClick={() => setPage((p) => Math.max(0, p - 1))}
          className="px-3 py-1 bg-slate-200 rounded disabled:opacity-50"
        >
          Précédent
        </button>
        <span>Page {page + 1}</span>
        <button
          disabled={!hasMore}
          onClick={() => setPage((p) => p + 1)}
          className="px-3 py-1 bg-slate-200 rounded disabled:opacity-50"
        >
          Suivant
        </button>
      </div>

      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/30 backdrop-blur-sm z-50">
          <div className="bg-white rounded shadow-lg w-full max-w-md p-6 relative transform-gpu scale-95 transition-all duration-200">
            <button
              className="absolute top-2 right-2 text-slate-600 hover:text-slate-900"
              onClick={() => setShowModal(false)}
            >
              ✕
            </button>
            <h2 className="text-xl font-semibold mb-4">
              {selected ? 'Éditer utilisateur' : 'Ajouter un utilisateur'}
            </h2>
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                try {
                  if (selected) {
                    await api.patch(`/users/${selected.id}`, form);
                  } else {
                    await api.post('/users', form);
                  }
                  setShowModal(false);
                  setForm({ email: '', username: '', role: 'patient', mot_de_passe: '' });
                  fetchUsers();
                } catch (err: any) {
                  alert(err.response?.data?.detail || 'Erreur');
                }
              }}
              className="space-y-4"
            >
              <input
                required
                type="email"
                placeholder="Email"
                className="w-full border px-3 py-2 rounded"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
              <input
                required
                type="text"
                placeholder="Username"
                className="w-full border px-3 py-2 rounded"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
              />
              {!selected && (
                <input
                  required
                  type="password"
                  placeholder="Mot de passe"
                  className="w-full border px-3 py-2 rounded"
                  value={form.mot_de_passe}
                  onChange={(e) => setForm({ ...form, mot_de_passe: e.target.value })}
                />
              )}
              <select
                className="w-full border px-3 py-2 rounded"
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
              >
                <option value="patient">patient</option>
                <option value="medecin">medecin</option>
                <option value="technicien">technicien</option>
                <option value="admin">admin</option>
              </select>
              <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded">
                {selected ? 'Enregistrer' : 'Créer'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
