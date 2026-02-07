'use client';

import { useEffect, useState } from 'react';
import { getTradingOverview } from '@/lib/api';
import { TrendingUp, Activity, Target, Volume2 } from 'lucide-react';

interface OverviewData {
  momentum_marche: { value: number; tendance: string };
  volatilite_moyenne: { value: number; status: string };
  signaux_actifs: { achat: number; vente: number; total: number };
  volume_relatif: { value: number; status: string };
}

export default function TradingOverview() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await getTradingOverview();
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
      title: 'Momentum Marché',
      value: `${data.momentum_marche.value}%`,
      subtitle: data.momentum_marche.tendance,
      icon: TrendingUp,
      color: data.momentum_marche.value > 50 ? 'text-green-600' : 'text-red-600',
    },
    {
      title: 'Volatilité Moyenne',
      value: `${(data.volatilite_moyenne.value * 100).toFixed(2)}%`,
      subtitle: data.volatilite_moyenne.status,
      icon: Activity,
      color: 'text-blue-600',
    },
    {
      title: 'Signaux Actifs',
      value: data.signaux_actifs.total,
      subtitle: `${data.signaux_actifs.achat} achats, ${data.signaux_actifs.vente} ventes`,
      icon: Target,
      color: 'text-purple-600',
    },
    {
      title: 'Volume Relatif',
      value: data.volume_relatif.value.toFixed(2),
      subtitle: data.volume_relatif.status,
      icon: Volume2,
      color: data.volume_relatif.status === 'Anormal' ? 'text-orange-600' : 'text-gray-600',
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
          <div className={`text-3xl font-bold ${card.color}`}>{card.value}</div>
          <p className="text-sm text-gray-500 mt-2">{card.subtitle}</p>
        </div>
      ))}
    </div>
  );
}