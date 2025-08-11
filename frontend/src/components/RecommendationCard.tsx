import React from 'react';
import { formatDistanceToNow } from 'date-fns/formatDistanceToNow';
import { fr } from 'date-fns/locale';

/**
 * Composant d'affichage d'une recommandation santé personnalisée.
 * Utilisé sur le tableau de bord Patient.
 * 
 * @param {Object} props - Les propriétés du composant
 * @param {string} props.titre - Titre de la recommandation (ex: "Hydratation")
 * @param {string} props.description - Description détaillée de la recommandation
 * @param {string} props.date - Date ISO de la recommandation
 * @param {string} [props.niveau] - Niveau d'importance (info, warning, urgent)
 */
interface Props {
  titre: string;
  description: string;
  date: string;
  niveau?: 'info' | 'warning' | 'urgent';
}

/**
 * Carte de recommandation avec mise en forme et icônes adaptées
 */
export default function RecommendationCard({ 
  titre, 
  description, 
  date,
  niveau = 'info' 
}: Props) {
  // Couleur de bordure en fonction du niveau
  const borderColors = {
    info: 'border-blue-500',
    warning: 'border-yellow-500',
    urgent: 'border-red-500'
  };

  // Icône en fonction du niveau
  const getIcon = () => {
    const iconClass = 'w-5 h-5 flex-shrink-0';
    
    switch(niveau) {
      case 'warning':
        return (
          <svg className={`${iconClass} text-yellow-500`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
      case 'urgent':
        return (
          <svg className={`${iconClass} text-red-500`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      default: // info
        return (
          <svg className={`${iconClass} text-blue-500`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  // Formatage de la date relative (ex: "il y a 2 jours")
  const formattedDate = formatDistanceToNow(new Date(date), { 
    addSuffix: true, 
    locale: fr 
  });

  return (
    <div 
      className={`flex flex-col h-full p-4 bg-white rounded-lg shadow-md border-l-4 ${borderColors[niveau]} hover:shadow-lg transition-shadow duration-200`}
      aria-label={`Recommandation : ${titre}`}
    >
      <div className="flex items-start gap-3 mb-2">
        <div className="mt-0.5">
          {getIcon()}
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-slate-800">
            {titre}
          </h3>
          <p className="mt-1 text-sm text-slate-600">
            {description}
          </p>
          <div className="mt-3 flex items-center text-xs text-slate-400">
            <svg className="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span title={new Date(date).toLocaleString('fr-FR')}>
              {formattedDate}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
