'use client';

import { useEffect, useState } from 'react';
import { getInvestmentOverview } from '@/lib/api';
import { TrendingUp, DollarSign, Shield, ArrowUpCircle } from 'lucide-react';
import KPITooltip from '@/components/KPITooltip';

interface OverviewData {
  qualite: { roe_moyen: number; marge_moyenne: number; status: string };
  croissance: { cagr_moyen: number; status: string };
  solidite: { score_moyen: number; dette_moyenne: number; status: string };
  dividendes: { rendement_moyen: number; status: string };
}

export default function InvestmentOverview() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await getInvestmentOverview();
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
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
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

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      
      {/* Card 1 : Qualité */}
      <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
        <div className="flex items-center justify-between mb-2">
          <div className="p-3 rounded-full bg-green-100 text-green-600">
            <Shield className="h-6 w-6" />
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            data.qualite.status === 'Excellente' ? 'bg-green-100 text-green-800' :
            data.qualite.status === 'Bonne' ? 'bg-blue-100 text-blue-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {data.qualite.status}
          </span>
        </div>
        <h3 className="text-gray-500 text-sm font-medium flex items-center">
          Qualité Moyenne du Marché
          <KPITooltip kpiKey="qualiteMarche" />
        </h3>
        <div className="mt-2">
          <div className="flex items-baseline">
            <p className="text-3xl font-bold text-gray-900">
              {data.qualite.roe_moyen.toFixed(1)}%
            </p>
            <span className="ml-2 text-sm text-gray-500">ROE</span>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Marge : {data.qualite.marge_moyenne.toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Card 2 : Croissance */}
      <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
        <div className="flex items-center justify-between mb-2">
          <div className="p-3 rounded-full bg-blue-100 text-blue-600">
            <ArrowUpCircle className="h-6 w-6" />
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            data.croissance.status === 'Forte' ? 'bg-green-100 text-green-800' :
            data.croissance.status === 'Modérée' ? 'bg-blue-100 text-blue-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {data.croissance.status}
          </span>
        </div>
        <h3 className="text-gray-500 text-sm font-medium flex items-center">
          Croissance Annuelle Moyenne
          <KPITooltip kpiKey="cagr" />
        </h3>
        <div className="mt-2">
          <div className="flex items-baseline">
            <p className="text-3xl font-bold text-gray-900">
              {data.croissance.cagr_moyen.toFixed(1)}%
            </p>
            <span className="ml-2 text-sm text-gray-500">CAGR</span>
          </div>
        </div>
      </div>

      {/* Card 3 : Solidité */}
      <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
        <div className="flex items-center justify-between mb-2">
          <div className="p-3 rounded-full bg-purple-100 text-purple-600">
            <Shield className="h-6 w-6" />
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            data.solidite.status === 'Solide' ? 'bg-green-100 text-green-800' :
            data.solidite.status === 'Modérée' ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            {data.solidite.status}
          </span>
        </div>
        <h3 className="text-gray-500 text-sm font-medium flex items-center">
          Solidité Financière Moyenne
          <KPITooltip kpiKey="soliditeMarche" />
        </h3>
        <div className="mt-2">
          <div className="flex items-baseline">
            <p className="text-3xl font-bold text-gray-900">
              {data.solidite.score_moyen.toFixed(0)}/100
            </p>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Dette/Equity : {data.solidite.dette_moyenne.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Card 4 : Dividendes */}
      <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
        <div className="flex items-center justify-between mb-2">
          <div className="p-3 rounded-full bg-amber-100 text-amber-600">
            <DollarSign className="h-6 w-6" />
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            data.dividendes.status === 'Élevé' ? 'bg-green-100 text-green-800' :
            data.dividendes.status === 'Moyen' ? 'bg-blue-100 text-blue-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {data.dividendes.status}
          </span>
        </div>
        <h3 className="text-gray-500 text-sm font-medium flex items-center">
          Rendement Dividendes Moyen
          <KPITooltip kpiKey="dividendesMarche" />
        </h3>
        <div className="mt-2">
          <div className="flex items-baseline">
            <p className="text-3xl font-bold text-gray-900">
              {data.dividendes.rendement_moyen.toFixed(2)}%
            </p>
          </div>
        </div>
      </div>

    </div>
  );
}