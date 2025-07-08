import { useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

export default function LoginRegister() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ email: '', username: '', password: '' });
  const [error, setError] = useState('');

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isLogin) {
        const { data } = await api.post('/auth/login', {
          identifiant: form.username || form.email,
          mot_de_passe: form.password,
        });
        localStorage.setItem('token', data.access_token);
      } else {
        const { data } = await api.post('/auth/register', {
          email: form.email,
          username: form.username,
          mot_de_passe: form.password,
        });
        localStorage.setItem('token', data.access_token);
      }
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur');
    }
  };

  return (
    <div className="container" style={{ maxWidth: 400, margin: '40px auto' }}>
      <h2>{isLogin ? 'Connexion' : "S'inscrire"}</h2>
      <form onSubmit={handleSubmit}>
        {!isLogin && (
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            required
          />
        )}
        <input
          type="text"
          name="username"
          placeholder="Nom d'utilisateur"
          value={form.username}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Mot de passe"
          value={form.password}
          onChange={handleChange}
          required
        />
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit">{isLogin ? 'Se connecter' : "S'inscrire"}</button>
      </form>
      <button onClick={toggleMode} style={{ marginTop: 10 }}>
        {isLogin ? "Pas de compte ? S'inscrire" : 'Déjà inscrit ? Se connecter'}
      </button>
    </div>
  );
}
