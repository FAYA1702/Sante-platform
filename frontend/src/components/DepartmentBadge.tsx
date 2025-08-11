import React from 'react';

interface DepartmentBadgeProps {
  departmentName?: string;
  departmentCode?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const DepartmentBadge: React.FC<DepartmentBadgeProps> = ({
  departmentName,
  departmentCode,
  className = '',
  size = 'md'
}) => {
  if (!departmentName && !departmentCode) {
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 ${className}`}>
        Non assigné
      </span>
    );
  }

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm'
  };

  const getColorClasses = (code?: string) => {
    if (!code) return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    
    switch (code.toUpperCase()) {
      case 'GENERAL':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'CARDIO':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      case 'OPHTALMO':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'DENTAIRE':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'PEDIATRIE':
        return 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300';
      case 'DERMATO':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${sizeClasses[size]} ${getColorClasses(departmentCode)} ${className}`}>
      {departmentCode ? `${departmentName} (${departmentCode})` : departmentName}
    </span>
  );
};

export default DepartmentBadge;
