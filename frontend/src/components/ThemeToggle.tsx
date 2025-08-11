import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSun, faMoon } from '@fortawesome/free-solid-svg-icons';

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-900 transition-colors"
      aria-label={theme === 'dark' ? 'Passer en mode clair' : 'Passer en mode sombre'}
    >
      {theme === 'dark' ? (
        <FontAwesomeIcon 
          icon={faSun} 
          className="w-5 h-5 text-yellow-400" 
        />
      ) : (
        <FontAwesomeIcon 
          icon={faMoon} 
          className="w-5 h-5 text-gray-700" 
        />
      )}
    </button>
  );
};

export default ThemeToggle;
