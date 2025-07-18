import React from 'react';

/**
 * Composant d'affichage d'une recommandation santé personnalisée.
 * Utilisé sur le tableau de bord Patient.
 * 
 * Props
 *  - titre : court titre (ex. « Hydratation »)
 *  - description : texte concis de la recommandation.
 *  - date : ISO string de la date de génération.
 */
interface Props {
  titre: string;
  description: string;
  date: string;
}

export default function RecommendationCard({ titre, description, date }: Props) {
  return (
    <div className="flex flex-col gap-1 p-4 bg-white rounded-lg shadow border-l-4 border-blue-500 max-w-md">
      <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
        {/* Icône ampoule */}
        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <path d="M9 18h6M10 22h4" />
          <path d="M12 2a7 7 0 0 0-4 12.9V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.1A7 7 0 0 0 12 2z" />
        </svg>
        {titre}
      </h3>
      <p className="text-sm text-slate-600">{description}</p>
      <span className="text-xs text-slate-400 mt-1">{new Date(date).toLocaleDateString('fr-FR')}</span>
    </div>
  );
}
