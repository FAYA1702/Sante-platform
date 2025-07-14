import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import React from 'react';

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend);

interface Props {
  labels: string[]; // formatted dates
  values: number[];
  label: string;
  color?: string;
}

/**
 * Génère un graphique <Line> avec les options par défaut ci-dessus.
 * Se contente de préparer l’objet `data` et `options`, le rendu est délégué au composant Line.
 */
export default function HealthChart({ labels, values, label, color = 'rgb(37,99,235)' }: Props) {
  const data = {
    labels,
    datasets: [
      {
        label,
        data: values,
        borderColor: color,
        backgroundColor: `${color.replace('rgb', 'rgba').replace(')', ',0.2)')}`,
        tension: 0.3,
        fill: true,
        pointRadius: 2,
      },
    ],
  };

  // Options Chart.js : responsif, légende cachée, axe X masqué (gain de place)
  const options = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        display: false,
      },
    },
  } as const;

  return <Line options={options} data={data} />;
}
