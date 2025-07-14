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
export default function StatsCard({ title, value, icon, color = 'blue' }: Props) {
  return (
    <div className={`flex items-center p-4 bg-white rounded-lg shadow w-full`}>
      {icon && (
        <div className={`p-3 rounded-full ${colorMap[color] || colorMap.blue} mr-4`}>{icon}</div>
      )}
      <div className="flex-1">
        <p className="text-sm text-slate-500">{title}</p>
        <p className="text-2xl font-semibold text-slate-800">{value}</p>
      </div>
    </div>
  );
}
