/**
 * Composant AdminApproval : Interface pour valider les médecins en attente
 */
import { useState, useEffect } from 'react';
import api from '../api';
import { StethoscopeIcon, CheckIcon, XMarkIcon } from './icons';

interface PendingDoctor {
  id: string;
  username: string;
  email: string;
  department_id: string;
  created_at: string;
  statut: string;
}

interface Department {
  id: string;
  name: string;
  code: string;
  description?: string;
}

export default function AdminApproval() {
  const [pendingDoctors, setPendingDoctors] = useState<PendingDoctor[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPendingDoctors();
    loadDepartments();
  }, []);

  const loadPendingDoctors = async () => {
    try {
      const { data } = await api.get('/admin/medecins-en-attente');
      setPendingDoctors(data);
    } catch (err: any) {
      setError('Erreur lors du chargement des médecins en attente');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadDepartments = async () => {
    try {
      // Utiliser les départements par défaut
      setDepartments([
        { id: 'default-general', name: 'Médecine Générale', code: 'GENERAL', description: 'Médecine générale' },
        { id: 'default-cardio', name: 'Cardiologie', code: 'CARDIO', description: 'Maladies cardiovasculaires' },
        { id: 'default-pneumo', name: 'Pneumologie', code: 'PNEUMO', description: 'Maladies respiratoires' }
      ]);
    } catch (err) {
      console.error('Erreur lors du chargement des départements:', err);
    }
  };

  const getDepartmentName = (departmentId: string) => {
    const dept = departments.find(d => d.id === departmentId);
    return dept ? dept.name : departmentId;
  };

  const approveDoctor = async (doctorId: string) => {
    try {
      console.log('Tentative d\'approbation du médecin:', doctorId);
      const response = await api.patch(`/admin/medecins/${doctorId}/approuver`);
      console.log('Réponse approbation:', response);
      await loadPendingDoctors(); // Recharger la liste
      setError(''); // Clear any previous errors
    } catch (err: any) {
      console.error('Erreur approbation:', err);
      setError(`Erreur lors de l'approbation: ${err.response?.data?.detail || err.message}`);
    }
  };

  const rejectDoctor = async (doctorId: string) => {
    try {
      console.log('Tentative de rejet du médecin:', doctorId);
      const response = await api.patch(`/admin/medecins/${doctorId}/rejeter`);
      console.log('Réponse rejet:', response);
      await loadPendingDoctors(); // Recharger la liste
      setError(''); // Clear any previous errors
    } catch (err: any) {
      console.error('Erreur rejet:', err);
      setError(`Erreur lors du rejet: ${err.response?.data?.detail || err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600 dark:text-gray-300">Chargement des médecins en attente...</div>
      </div>
    );
  }

  return (
    <div className="h-full">

      {error && (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 text-red-800 px-4 py-3 dark:bg-red-900/20 dark:border-red-800 dark:text-red-200">
          {error}
        </div>
      )}

      {pendingDoctors.length === 0 ? (
        <div className="flex items-center p-4 bg-white rounded-lg shadow w-full min-h-[88px]">
          <div className="p-3 rounded-full bg-emerald-100 text-emerald-600 mr-4 flex items-center justify-center">
            <CheckIcon className="h-5 w-5" />
          </div>
          <div className="flex-1">
            <p className="text-sm text-slate-500">Validations</p>
            <p className="text-2xl font-semibold text-slate-800">0</p>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow w-full overflow-hidden">
          <div className="px-3 py-2 border-b border-gray-200">
            <h3 className="text-xs font-medium text-gray-900 flex items-center gap-1 truncate">
              <StethoscopeIcon className="h-3 w-3 text-blue-600 flex-shrink-0" />
              Médecins en attente ({pendingDoctors.length})
            </h3>
          </div>
          <div className="max-h-32 overflow-y-auto">
            {pendingDoctors.map((doctor, index) => (
              <div key={doctor.id} className="p-2 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center space-x-2 min-w-0 flex-1">
                    <div className="h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <span className="text-blue-700 font-medium text-xs">
                        {doctor.username.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="text-xs font-medium text-gray-900 truncate">
                        Dr. {doctor.username}
                      </div>
                      <div className="text-xs text-gray-500 truncate">
                        {doctor.email}
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-1 flex-shrink-0">
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('Clic approuver pour:', doctor.id);
                        approveDoctor(doctor.id);
                      }}
                      className="bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded text-xs font-medium transition-colors focus:outline-none focus:ring-1 focus:ring-offset-1 focus:ring-green-500 inline-flex items-center gap-1"
                      title="Approuver"
                    >
                      <CheckIcon className="h-3 w-3" />
                      <span className="hidden sm:inline">Approuver</span>
                    </button>
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('Clic rejeter pour:', doctor.id);
                        rejectDoctor(doctor.id);
                      }}
                      className="bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-xs font-medium transition-colors focus:outline-none focus:ring-1 focus:ring-offset-1 focus:ring-red-500 inline-flex items-center gap-1"
                      title="Rejeter"
                    >
                      <XMarkIcon className="h-3 w-3" />
                      <span className="hidden sm:inline">Rejeter</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Note supprimée pour affichage compact dans le dashboard */}
    </div>
  );
}
