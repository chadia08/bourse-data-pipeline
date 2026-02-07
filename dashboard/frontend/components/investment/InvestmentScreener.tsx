'use client';

import { useEffect, useState } from 'react';
import { getInvestmentScreener } from '@/lib/api';
import { Filter } from 'lucide-react';
import KPITooltip from '../KPITooltip';

interface Stock {
  symbole: string;
  nom: string;
  secteur: string;
  roe: number;
  marge: number;
  dette: number;
  dividendes: number;
  cagr: number;
  score: number;
}

export default function InvestmentScreener() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [strategy, setStrategy] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const params = strategy ? { strategy } : undefined;
        const data = await getInvestmentScreener(params);
        setStocks(data);
      } catch (error) {
        console.error('Erreur:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [strategy]);

  const strategies = [
    { id: '', label: 'Toutes', desc: 'Sans filtre' },
    { id: 'value', label: 'Value', desc: 'ROE>15%, Dette<0.5' },
    { id: 'dividend', label: 'Dividendes', desc: 'Rendement>3%' },
    { id: 'growth', label: 'Croissance', desc: 'CAGR>20%' },
    { id: 'quality', label: 'Qualité', desc: 'Score>80' },
  ];

  const getScoreBadge = (score: number) => {
    if (score >= 80) return 'bg-green-100 text-green-800';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  if (loading) {
    return <div className="bg-white rounded-lg shadow p-6">Chargement...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-6 border-b">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-600" />
            <h2 className="text-xl font-bold">Screener Fondamental</h2>
          </div>
          <span className="text-sm text-gray-500">{stocks.length} résultats</span>
        </div>
        
        <div className="flex gap-2 flex-wrap">
          {strategies.map((strat) => (
            <button
              key={strat.id}
              onClick={() => setStrategy(strat.id)}
              className={`px-4 py-2 rounded-lg transition ${
                strategy === strat.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 hover:bg-gray-200'
              }`}
            >
              <div className="font-medium">{strat.label}</div>
              <div className="text-xs opacity-75">{strat.desc}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbole<KPITooltip kpiKey="symbole" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom <KPITooltip kpiKey="nom" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Secteur<KPITooltip kpiKey="secteur" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ROE <KPITooltip kpiKey="roe" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Marge   <KPITooltip kpiKey="marge" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dette <KPITooltip kpiKey="dette" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dividendes<KPITooltip kpiKey="dividendes" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">CAGR<KPITooltip kpiKey="cagr" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score<KPITooltip kpiKey="score" /></th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {stocks.map((stock) => (
              <tr key={stock.symbole} className="hover:bg-gray-50">
                <td className="px-6 py-4 font-medium text-blue-600">{stock.symbole}</td>
                <td className="px-6 py-4 text-sm text-gray-900">{stock.nom}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{stock.secteur}</td>
                <td className="px-6 py-4">
                  <span className={stock.roe > 15 ? 'text-green-600 font-medium' : ''}>
                    {stock.roe.toFixed(1)}%
                  </span>
                </td>
                <td className="px-6 py-4">{stock.marge.toFixed(1)}%</td>
                <td className="px-6 py-4">
                  <span className={stock.dette < 0.5 ? 'text-green-600' : 'text-orange-600'}>
                    {stock.dette.toFixed(2)}
                  </span>
                </td>
                <td className="px-6 py-4">{stock.dividendes.toFixed(2)}%</td>
                <td className="px-6 py-4">
                  <span className={stock.cagr > 10 ? 'text-green-600 font-medium' : ''}>
                    {stock.cagr.toFixed(1)}%
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreBadge(stock.score)}`}>
                    {stock.score}/100
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}