/**
 * Loader.tsx — Composant loader animé (spinner médical)
 * Utilisé pour indiquer le chargement des données (dashboard, alertes, etc.)
 */
import React from 'react';

export default function Loader() {
  return (
    <div className="flex flex-col items-center justify-center py-8">
      {/* Spinner SVG */}
      <svg className="animate-spin h-10 w-10 text-blue-600 mb-2" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
      <span className="text-blue-700 text-sm mt-1">Chargement...</span>
    </div>
  );
}
