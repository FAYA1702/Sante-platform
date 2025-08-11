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
  timeout: 10000, // 10 secondes de timeout
});

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

// Intercepteur pour gérer les erreurs globales
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Erreurs 4xx/5xx
      console.error('Erreur API:', error.response.status, error.response.data);
      
      // Gestion spécifique des erreurs d'authentification
      if (error.response.status === 401) {
        // Rediriger vers la page de connexion si le token est invalide/expiré
        if (window.location.pathname !== '/login') {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
      }
    } else if (error.request) {
      // La requête a été faite mais aucune réponse n'a été reçue
      console.error('Pas de réponse du serveur:', error.request);
    } else {
      // Erreur lors de la configuration de la requête
      console.error('Erreur de configuration:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;
