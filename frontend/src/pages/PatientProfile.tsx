import React, { useState, useEffect } from 'react';
import api from '../api';
import Loader from '../components/Loader';

interface MedecinReferent {
  id: string;
  username: string;
  email: string;
  nom?: string;
  prenom?: string;
  department_id?: string;
}

const PatientProfile: React.FC = () => {
  const [medecin, setMedecin] = useState<MedecinReferent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Vérifier que l'utilisateur est un patient
  let role = '';
  let username = '';
  try {
    const payload = JSON.parse(atob(localStorage.getItem('token')?.split('.')[1] || ''));
    role = payload.role || '';
    username = payload.username || '';
  } catch {}

  useEffect(() => {
    if (role !== 'patient') return;
    
    fetchMedecinReferent();
  }, [role]);

  const fetchMedecinReferent = async () => {
    try {
      setLoading(true);
      const response = await api.get('/patient/medecin-referent');
      setMedecin(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement du médecin référent');
    } finally {
      setLoading(false);
    }
  };

  if (role !== 'patient') {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="bg-red-100 border border-red-300 text-red-800 px-6 py-4 rounded-lg">
          Accès réservé aux patients
        </div>
      </div>
    );
  }

  if (loading) return <Loader />;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          👤 Mon Profil Patient
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Informations sur votre suivi médical
        </p>
      </div>

      {/* Informations patient */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          📋 Mes Informations
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Nom d'utilisateur
            </label>
            <p className="mt-1 text-lg text-gray-900 dark:text-white">{username}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Statut
            </label>
            <span className="mt-1 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
              ✅ Télésurveillance active
            </span>
          </div>
        </div>
      </div>

      {/* Médecin référent */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          👨‍⚕️ Mon Médecin Référent
        </h2>
        
        {error && (
          <div className="bg-red-100 border border-red-300 text-red-800 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {!medecin && !error ? (
          <div className="bg-yellow-100 border border-yellow-300 text-yellow-800 px-4 py-3 rounded">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="font-medium">Aucun médecin assigné</p>
                <p className="text-sm">Contactez l'administration pour vous assigner un médecin référent.</p>
              </div>
            </div>
          </div>
        ) : medecin ? (
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  {medecin.nom && medecin.prenom 
                    ? `Dr. ${medecin.prenom} ${medecin.nom}`
                    : `Dr. ${medecin.username}`
                  }
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {medecin.email}
                </p>
                {medecin.department_id && (
                  <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    <span className="capitalize">
                      {medecin.department_id === 'cardiologie' ? '❤️ Cardiologie' :
                       medecin.department_id === 'pneumologie' ? '🫁 Pneumologie' :
                       medecin.department_id === 'medecine_generale' ? '🏥 Médecine Générale' :
                       medecin.department_id}
                    </span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center text-sm text-green-600 dark:text-green-400">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Médecin référent pour votre télésurveillance
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Actions rapides */}
      <div className="mt-6 bg-gray-50 dark:bg-gray-900 rounded-xl p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          🔗 Actions rapides
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => window.location.href = '/data'}
            className="flex items-center p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <svg className="w-5 h-5 text-blue-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4" />
            </svg>
            <div className="text-left">
              <p className="font-medium text-gray-900 dark:text-white">Mes Données</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Consulter mes paramètres vitaux</p>
            </div>
          </button>
          
          <button
            onClick={() => window.location.href = '/recommendations'}
            className="flex items-center p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <div className="text-left">
              <p className="font-medium text-gray-900 dark:text-white">Recommandations</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Voir les conseils de mon médecin</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PatientProfile;
