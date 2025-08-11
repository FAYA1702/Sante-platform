import React, { useState, useEffect } from 'react';
import { Department, departmentService } from '../services/departmentService';

interface DepartmentFilterProps {
  selectedDepartment: string | null;
  onDepartmentChange: (departmentId: string | null) => void;
  className?: string;
}

const DepartmentFilter: React.FC<DepartmentFilterProps> = ({
  selectedDepartment,
  onDepartmentChange,
  className = ''
}) => {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDepartments = async () => {
      try {
        setLoading(true);
        const data = await departmentService.getDepartments();
        setDepartments(data);
        setError(null);
      } catch (err) {
        console.error('Erreur lors du chargement des départements:', err);
        setError('Impossible de charger les départements');
      } finally {
        setLoading(false);
      }
    };

    loadDepartments();
  }, []);

  if (loading) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
        <span className="text-sm text-gray-500 dark:text-gray-400">Chargement...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`text-sm text-red-600 dark:text-red-400 ${className}`}>
        {error}
      </div>
    );
  }

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <label htmlFor="department-filter" className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Département :
      </label>
      <select
        id="department-filter"
        value={selectedDepartment || ''}
        onChange={(e) => onDepartmentChange(e.target.value || null)}
        className="block w-48 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
      >
        <option value="">Tous les départements</option>
        {departments.map((dept) => (
          <option key={dept.id} value={dept.id}>
            {dept.name} ({dept.code})
          </option>
        ))}
      </select>
    </div>
  );
};

export default DepartmentFilter;
