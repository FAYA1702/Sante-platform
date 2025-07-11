import axios from 'axios';

const api = axios.create({
  baseURL: (import.meta as any).env.VITE_API_URL || 'http://localhost:8000',
});

// Ajout d'un interceptor pour attacher le JWT si présent
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    // Axios v1 : config.headers est de type AxiosHeaders ; on utilise set()
    if (typeof (config.headers as any).set === 'function') {
      (config.headers as any).set('Authorization', `Bearer ${token}`);
    } else {
      // Fallback pour l'ancien type (objet simple)
      (config.headers as any)['Authorization'] = `Bearer ${token}`;
    }
  }
  return config;
});

export default api;
