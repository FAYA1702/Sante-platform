import React from 'react';

/**
 * Composant alerte RBAC : affiche un message d’accès refusé (UX moderne).
 * Utilisé pour informer l’utilisateur qu’il n’a pas le droit d’accéder à une page protégée.
 */
export default function AlertRBAC({ message }: { message: string }) {
  return (
    <div className="fixed top-6 left-1/2 transform -translate-x-1/2 z-50 bg-red-100 border border-red-300 text-red-800 px-6 py-3 rounded shadow-lg flex items-center gap-3 animate-fade-in">
      <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" className="fill-red-200" />
        <path d="M12 8v4m0 4h.01" strokeLinecap="round" />
      </svg>
      <span className="font-semibold">{message}</span>
    </div>
  );
}

// Animation fade-in (à ajouter dans index.css ou tailwind.config.js si besoin)
// .animate-fade-in { animation: fadeIn .5s; }
// @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
