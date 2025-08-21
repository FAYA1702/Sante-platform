import axios from 'axios';

/**
 * Instance Axios configurée pour communiquer avec l'API FastAPI.
 * 
 * Configuration :
 * - Base URL définie via VITE_API_URL ou localhost:8000 par défaut
 * - En-tête Content-Type défini sur application/json
 * - Intercepteur pour ajouter automatiquement le token JWT
 * - Gestion des erreurs de base
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 secondes de timeout pour éviter les erreurs lors d'ajout de données
});

// Log de diagnostic: baseURL effective
console.info('[API] baseURL =', api.defaults.baseURL);

// Intercepteur pour ajouter le token JWT à chaque requête
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs globales avec retry automatique
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    // Ne pas bruiter la console si la requête a été annulée (StrictMode/cleanup)
    if ((error as any)?.code === 'ERR_CANCELED' || error.message?.toLowerCase().includes('canceled')) {
      return Promise.reject(error);
    }
    
    if (error.response) {
      // Erreurs 4xx/5xx
      console.error('[API] Erreur HTTP:', error.response.status, error.response.data);
      
      // Gestion spécifique des erreurs d'authentification
      if (error.response.status === 401) {
        // Vider complètement le localStorage et rediriger
        localStorage.clear();
        if (window.location.pathname !== '/auth' && window.location.pathname !== '/login') {
          window.location.href = '/auth';
        }
      }
    } else if (error.request) {
      // La requête a été faite mais aucune réponse n'a été reçue (timeout/réseau/CORS)
      console.error('[API] Pas de réponse du serveur. Détails:', {
        method: originalRequest?.method,
        url: originalRequest?.url,
        baseURL: originalRequest?.baseURL,
        timeout: originalRequest?.timeout,
        withCredentials: originalRequest?.withCredentials,
        code: (error as any)?.code,
        message: error.message,
        online: navigator.onLine,
      });
      
      // Retry automatique pour les timeouts (max 2 tentatives)
      if (!originalRequest._retry && (error.code === 'ECONNABORTED' || error.message.includes('timeout'))) {
        originalRequest._retry = true;
        console.log('[API] 🔄 Nouvelle tentative (timeout)...');
        
        // Attendre 1 seconde avant de réessayer
        await new Promise(resolve => setTimeout(resolve, 1000));
        return api(originalRequest);
      }
    } else {
      // Erreur lors de la configuration de la requête
      console.error('[API] Erreur de configuration:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;
