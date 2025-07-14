/**
 * Page « LoginRegister » : gère à la fois l’inscription et la connexion.
 *
 * 1. Mode connexion (`isLogin=true`) : appelle `/auth/login` et stocke le JWT.
 * 2. Mode inscription (`isLogin=false`) : appelle `/auth/register`, puis connecte automatiquement l’utilisateur.
 * 3. Une fois authentifié, le token est enregistré dans `localStorage` puis l’utilisateur est redirigé vers le Dashboard (`/`).
 *
 * Les champs affichés varient selon le mode :
 *  - Inscription : email + username + mot de passe
 *  - Connexion  : username (ou email) + mot de passe
 */
import { useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

export default function LoginRegister() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ email: '', username: '', password: '', role: 'patient' });
  const [error, setError] = useState('');

  // ⇄ Bascule entre les modes Connexion et Inscription
  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // ➜ Soumission du formulaire : appel API adapté au mode (login / register)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isLogin) {
        const { data } = await api.post('/auth/login', {
          identifiant: form.username || form.email,
          mot_de_passe: form.password,
        });
        // Stocker le JWT pour les prochains appels protégés
        localStorage.setItem('token', data.access_token);
      } else {
        const { data } = await api.post('/auth/register', {
          email: form.email,
          username: form.username,
          mot_de_passe: form.password,
          role: form.role, // On envoie le rôle choisi (patient ou medecin)
        });
        // Stocker le JWT pour les prochains appels protégés
        localStorage.setItem('token', data.access_token);
      }
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 to-slate-200">  
      <div className="w-full max-w-sm bg-white/80 backdrop-blur rounded-xl shadow-lg p-8">
      <h2 className="text-center text-2xl font-semibold mb-6">
        {isLogin ? 'Connexion' : 'Inscription'}
      </h2>
  
      {error && <p className="text-red-600 mb-3">{error}</p>}
  
      <form onSubmit={handleSubmit} className="space-y-3">
        {!isLogin && (
          <>
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={form.email}
              onChange={handleChange}
              required
              className="w-full border px-3 py-2 rounded"
            />
            {/* Champ de sélection du rôle */}
            <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="role">
              Rôle <span title="Le patient peut consulter ses propres données. Le médecin peut consulter les données de ses patients.">(?)</span>
            </label>
            <select
              id="role"
              name="role"
              value={form.role}
              onChange={e => setForm({ ...form, role: e.target.value })}
              className="w-full border px-3 py-2 rounded"
              required
              title="Le patient peut consulter ses propres données. Le médecin peut consulter les données de ses patients."
            >
              <option value="patient">Patient</option>
              <option value="medecin">Médecin</option>
            </select>
            <p className="text-xs text-slate-500 mt-1">Le patient accède à ses données personnelles. Le médecin accède à celles de ses patients.</p>
          </>
        )}
  
        <input
          type="text"
          name="username"
          placeholder="Nom d'utilisateur"
          value={form.username}
          onChange={handleChange}
          required
          className="w-full border px-3 py-2 rounded"
        />
  
        <input
          type="password"
          name="password"
          placeholder="Mot de passe"
          value={form.password}
          onChange={handleChange}
          required
          className="w-full border px-3 py-2 rounded"
        />
  
        <button
          type="submit"
          className="w-full py-2 rounded bg-gradient-to-r from-blue-500 to-blue-700 hover:opacity-90 text-white font-semibold"
        >
          {isLogin ? 'Se connecter' : "S'inscrire"}
        </button>
      </form>
  
      <button
        onClick={toggleMode}
        className="mt-4 text-center text-sm text-slate-600 hover:text-blue-600 w-full"
      >
        {isLogin ? "Pas de compte ? S'inscrire" : 'Déjà inscrit ? Se connecter'}
      </button>
      </div>
    </div>
  );
}