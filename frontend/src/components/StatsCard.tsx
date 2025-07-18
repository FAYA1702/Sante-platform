/**
 * Composant d’affichage d’une statistique (nombre d’appareils, d’utilisateurs, etc.).
 * 
 * Props
 *  - title : libellé (ex. « Appareils »)
 *  - value : nombre ou texte à afficher en gras
 *  - icon  : icône optionnelle à gauche
 *  - color : couleur Tailwind pour la pastille d’icône (blue, green, red, yellow)
 */
import React from 'react';

interface Props {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  color?: string; // Tailwind color name e.g. 'blue', 'green'
}

// Dictionnaire simple pour associer un nom de couleur Tailwind à ses classes de fond/texte
const colorMap: Record<string, string> = {
  blue: 'bg-blue-100 text-blue-600',
  green: 'bg-green-100 text-green-600',
  red: 'bg-red-100 text-red-600',
  yellow: 'bg-yellow-100 text-yellow-600',
};

/**
 * Le composant est volontairement « stateless » : tout vient des props.
 * Il applique une mise en forme cohérente sur fond blanc avec ombre légère.
 */
function getIcon(title: string) {
  switch (title) {
    case 'Appareils':
      // Stéthoscope (bleu)
      return (
        <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <path d="M6 3v7a6 6 0 0 0 12 0V3" strokeLinecap="round"/>
          <circle cx="18" cy="19" r="3"/>
          <circle cx="6" cy="19" r="3"/>
          <path d="M6 19h12"/>
        </svg>
      );
    case 'Données':
      // Dossier médical (vert)
      return (
        <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <rect x="3" y="7" width="18" height="13" rx="2"/>
          <path d="M3 7V5a2 2 0 0 1 2-2h3l2 2h9a2 2 0 0 1 2 2v2"/>
        </svg>
      );
    case 'Alertes':
      // Cloche alerte (rouge)
      return (
        <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
      );
    case 'Utilisateurs':
      // Utilisateurs (jaune)
      return (
        <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <circle cx="12" cy="7" r="4"/>
          <path d="M5.5 21a7.5 7.5 0 0 1 13 0"/>
        </svg>
      );
    default:
      return null;
  }
}

export default function StatsCard({ title, value, color = 'blue' }: Props) {
  return (
    <div className={`flex items-center p-4 bg-white rounded-lg shadow w-full`}>
      <div className={`p-3 rounded-full ${colorMap[color] || colorMap.blue} mr-4 flex items-center justify-center`}>
        {getIcon(title)}
      </div>
      <div className="flex-1">
        <p className="text-sm text-slate-500">{title}</p>
        <p className="text-2xl font-semibold text-slate-800">{value}</p>
      </div>
    </div>
  );
}
