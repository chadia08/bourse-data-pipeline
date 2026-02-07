'use client';

import { useEffect, useState } from 'react';
import { getTradingSignals } from '@/lib/api';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';
import KPITooltip from '@/components/KPITooltip';

interface Signal {
  symbole: string;
  signal: string;
  force: number;
  confiance: string;
  raisons: string[];
  rsi: number;
  macd: number;
  volume_relatif: number;
  prix_actuel: number;
  variation: number;
}

export default function SignalsTable() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [filter, setFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSignals() {
      try {
        const data = await getTradingSignals(filter || undefined);
        setSignals(data);
      } catch (error) {
        console.error('Erreur:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchSignals();
  }, [filter]);

  const getSignalBadge = (signal: string) => {
    const styles = {
      Achat: 'bg-green-100 text-green-800',
      Vente: 'bg-red-100 text-red-800',
      Neutre: 'bg-gray-100 text-gray-800',
    };
    return styles[signal as keyof typeof styles] || styles.Neutre;
  };

  const getStars = (force: number) => {
    return '⭐'.repeat(force);
  };

  if (loading) {
    return <div className="bg-white rounded-lg shadow p-6">Chargement...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-6 border-b">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">Signaux de Trading</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('')}
              className={`px-4 py-2 rounded ${!filter ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}
            >
              Tous
            </button>
            <button
              onClick={() => setFilter('Achat')}
              className={`px-4 py-2 rounded ${filter === 'Achat' ? 'bg-green-600 text-white' : 'bg-gray-100'}`}
            >
              Achat
            </button>
            <button
              onClick={() => setFilter('Vente')}
              className={`px-4 py-2 rounded ${filter === 'Vente' ? 'bg-red-600 text-white' : 'bg-gray-100'}`}
            >
              Vente
            </button>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbole</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Signal<KPITooltip kpiKey="signal" showDisclaimer /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Force<KPITooltip kpiKey="force" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">RSI<KPITooltip kpiKey="rsi" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">MACD<KPITooltip kpiKey="macd" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vol. Relatif<KPITooltip kpiKey="volumeRelatif" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prix<KPITooltip kpiKey="prix" /></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Variation<KPITooltip kpiKey="variation" /></th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {signals.map((signal) => (
              <tr key={signal.symbole} className="hover:bg-gray-50">
                <td className="px-6 py-4 font-medium text-blue-600">{signal.symbole}</td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSignalBadge(signal.signal)}`}>
                    {signal.signal}
                  </span>
                </td>
                <td className="px-6 py-4">{getStars(signal.force)}</td>
                <td className="px-6 py-4">
                  <span
                    className={`font-medium ${
                      signal.rsi < 30 ? 'text-green-600' : signal.rsi > 70 ? 'text-red-600' : 'text-gray-600'
                    }`}
                  >
                    {signal.rsi.toFixed(2)}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={signal.macd > 0 ? 'text-green-600' : 'text-red-600'}>
                    {signal.macd > 0 ? '↗' : '↘'} {signal.macd.toFixed(4)}
                  </span>
                </td>
                <td className="px-6 py-4">{signal.volume_relatif.toFixed(2)}x</td>
                <td className="px-6 py-4">{signal.prix_actuel.toFixed(2)} $</td>
                <td className="px-6 py-4">
                  <span className={signal.variation >= 0 ? 'text-green-600' : 'text-red-600'}>
                    {signal.variation >= 0 ? '↑' : '↓'} {Math.abs(signal.variation).toFixed(2)}%
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