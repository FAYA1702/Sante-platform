/**
 * Composant AdminApproval : Interface pour valider les médecins en attente
 */
import { useState, useEffect } from 'react';
import api from '../api';

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
      await api.patch(`/admin/medecins/${doctorId}/approuver`);
      await loadPendingDoctors(); // Recharger la liste
    } catch (err: any) {
      setError('Erreur lors de l\'approbation du médecin');
      console.error(err);
    }
  };

  const rejectDoctor = async (doctorId: string) => {
    try {
      await api.patch(`/admin/medecins/${doctorId}/rejeter`);
      await loadPendingDoctors(); // Recharger la liste
    } catch (err: any) {
      setError('Erreur lors du rejet du médecin');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600">Chargement des médecins en attente...</div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        Validation des médecins en attente
      </h2>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {pendingDoctors.length === 0 ? (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          <p className="font-medium">Aucun médecin en attente de validation</p>
          <p className="text-sm">Tous les médecins inscrits ont été traités.</p>
        </div>
      ) : (
        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Médecin
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Spécialité
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date d'inscription
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {pendingDoctors.map((doctor) => (
                <tr key={doctor.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-blue-600 font-medium text-sm">
                            {doctor.username.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          Dr. {doctor.username}
                        </div>
                        <div className="text-sm text-gray-500">
                          ID: {doctor.id}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {doctor.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {getDepartmentName(doctor.department_id)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(doctor.created_at).toLocaleDateString('fr-FR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => approveDoctor(doctor.id)}
                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm transition-colors"
                      >
                        ✓ Approuver
                      </button>
                      <button
                        onClick={() => rejectDoctor(doctor.id)}
                        className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition-colors"
                      >
                        ✗ Rejeter
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-6 text-sm text-gray-600">
        <p><strong>Note :</strong> Les médecins approuvés pourront immédiatement accéder à la plateforme et consulter leurs patients assignés.</p>
        <p>Les médecins rejetés devront contacter l'administration pour plus d'informations.</p>
      </div>
    </div>
  );
}
