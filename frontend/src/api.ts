/**
 * Instance Axios centralisée pour communiquer avec l’API FastAPI.
 * 
 * Avantages :
 *  - BaseURL définie une seule fois (lue dans les variables Vite `VITE_API_URL`).
 *  - Intercepteur request : attache automatiquement le JWT enregistré dans `localStorage`.
 *    Ainsi, tous les appels protégés n’ont pas besoin de répéter l’entête `Authorization`.
 */
import axios from 'axios';

const api = axios.create({
  baseURL: (import.meta as any).env.VITE_API_URL || 'http://localhost:8000',
});

// ➜ Intercepteur : si un token est présent, on l’ajoute sous la forme
//    `Authorization: Bearer <token>` avant l’envoi de la requête.
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
