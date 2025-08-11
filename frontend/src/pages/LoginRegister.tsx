/**
 * Page « LoginRegister » : gère à la fois l'inscription et la connexion.
 * VERSION SIMPLIFIÉE POUR DEBUG
 */
import { useState, useEffect } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

interface Department {
  id: string;
  name: string;
  code: string;
  description?: string;
}

export default function LoginRegister() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ email: '', username: '', password: '', role: 'patient', department_id: '' });
  const [error, setError] = useState('');
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loadingDepartments, setLoadingDepartments] = useState(false);

  // Fonction handleChange pour tous les champs du formulaire
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Charger les départements pour les patients ET médecins
  useEffect(() => {
    if (!isLogin && (form.role === 'patient' || form.role === 'medecin')) {
      loadDepartments();
    }
  }, [isLogin, form.role]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadDepartments = async () => {
    try {
      setLoadingDepartments(true);
      // Utiliser directement les départements par défaut pour éviter les erreurs API
      setDepartments([
        { id: 'default-general', name: 'Médecine Générale', code: 'GENERAL', description: 'Médecine générale' },
        { id: 'default-cardio', name: 'Cardiologie', code: 'CARDIO', description: 'Maladies cardiovasculaires' },
        { id: 'default-pneumo', name: 'Pneumologie', code: 'PNEUMO', description: 'Maladies respiratoires' }
      ]);
    } catch (error) {
      console.error('Erreur lors du chargement des départements:', error);
    } finally {
      setLoadingDepartments(false);
    }
  };

  // ⇄ Bascule entre les modes Connexion et Inscription
  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
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
        const registerData: any = {
          email: form.email,
          username: form.username,
          mot_de_passe: form.password,
          role: form.role,
        };
        
        // Ajouter le département si c'est un patient ou un médecin
        if ((form.role === 'patient' || form.role === 'medecin') && form.department_id) {
          registerData.department_id = form.department_id;
        }
        
        const { data } = await api.post('/auth/register', registerData);
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
              onChange={e => setForm({ ...form, role: e.target.value, department_id: '' })}
              className="w-full border px-3 py-2 rounded"
              required
              title="Le patient peut consulter ses propres données. Le médecin peut consulter les données de ses patients."
            >
              <option value="patient">Patient</option>
              <option value="medecin">Médecin</option>
            </select>
            <p className="text-xs text-slate-500 mt-1">Le patient accède à ses données personnelles. Le médecin accède à celles de ses patients.</p>
            
            {/* Sélection du département pour les patients et médecins */}
            {(form.role === 'patient' || form.role === 'medecin') && (
              <>
                <label className="block text-sm font-medium text-slate-700 mb-1 mt-3" htmlFor="department">
                  {form.role === 'patient' ? 'Département médical' : 'Spécialité médicale'} 
                  <span title={form.role === 'patient' ? 
                    "Choisissez le département médical selon votre besoin de suivi" : 
                    "Choisissez votre spécialité médicale"}>(?)</span>
                </label>
                {loadingDepartments ? (
                  <div className="w-full border px-3 py-2 rounded bg-gray-100 text-gray-500">
                    Chargement des départements...
                  </div>
                ) : (
                  <select
                    id="department"
                    name="department_id"
                    value={form.department_id}
                    onChange={handleChange}
                    className="w-full border px-3 py-2 rounded"
                    required
                    title={form.role === 'patient' ? 
                      "Choisissez le département médical selon votre besoin de suivi" : 
                      "Choisissez votre spécialité médicale"}
                  >
                    <option value="">
                      {form.role === 'patient' ? 'Sélectionnez un département' : 'Sélectionnez votre spécialité'}
                    </option>
                    {departments.map(dept => (
                      <option key={dept.id} value={dept.id}>
                        {dept.name} {dept.description && `- ${dept.description}`}
                      </option>
                    ))}
                  </select>
                )}
                <p className="text-xs text-slate-500 mt-1">
                  {form.role === 'patient' ? 
                    'Un médecin spécialisé vous sera automatiquement attribué selon votre choix.' :
                    'Votre compte sera soumis à validation par un administrateur avant activation.'}
                </p>
              </>
            )}
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