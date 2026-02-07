'use client';

import { useEffect, useState } from 'react';
import { getPredictionsOverview } from '@/lib/api';
import { Brain, TrendingUp, Calendar, Activity } from 'lucide-react';

interface OverviewData {
  actions_disponibles: number;
  modele: string;
  type: string;
  horizon: string;
  status: string;
}

export default function PredictionsOverview() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await getPredictionsOverview();
        setData(result);
      } catch (error) {
        console.error('Erreur:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!data) return null;

  const cards = [
    {
      title: 'Actions Disponibles',
      value: data.actions_disponibles,
      subtitle: 'Avec historique > 1 an',
      icon: Activity,
      color: 'text-blue-600',
    },
    {
      title: 'Modèle ML',
      value: data.modele,
      subtitle: data.type,
      icon: Brain,
      color: 'text-purple-600',
    },
    {
      title: 'Horizon de Prédiction',
      value: data.horizon,
      subtitle: 'Prévisions futures',
      icon: Calendar,
      color: 'text-green-600',
    },
    {
      title: 'Statut du Modèle',
      value: data.status,
      subtitle: data.status === 'Actif' ? 'Prêt à prédire' : 'Indisponible',
      icon: TrendingUp,
      color: data.status === 'Actif' ? 'text-green-600' : 'text-red-600',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      {cards.map((card, index) => (
        <div key={index} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600">{card.title}</h3>
            <card.icon className={`w-5 h-5 ${card.color}`} />
          </div>
          <div className={`text-2xl font-bold ${card.color} mb-1`}>{card.value}</div>
          <p className="text-sm text-gray-500">{card.subtitle}</p>
        </div>
      ))}
    </div>
  );
}