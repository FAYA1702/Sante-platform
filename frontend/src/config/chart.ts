// src/config/chart.ts
// Enregistre globalement les plugins et éléments Chart.js utilisés par l'application.
// Ceci doit être importé une seule fois (dans App.tsx) afin que les graphiques fonctionnent.

import {
  Chart,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  TimeScale,
  TimeSeriesScale,
} from 'chart.js';

// Enregistrement global des composants et plugins nécessaires
Chart.register(
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  TimeScale,
  TimeSeriesScale,
);

// Optionnel : configuration par défaut
Chart.defaults.font.family = 'Inter, sans-serif';
Chart.defaults.color = '#374151'; // Slate-700

export default Chart;
