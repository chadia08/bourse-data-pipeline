'use client';

import { useEffect, useState } from 'react';
import { getTopMovers } from '@/lib/api';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface Mover {
  Symbole: string;
  Prix: number;
  Variation_PCT: number;
  Volume: number;
}

export default function TopMovers() {
  const [hausses, setHausses] = useState<Mover[]>([]);
  const [baisses, setBaisses] = useState<Mover[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchMovers() {
      try {
        const data = await getTopMovers();
        setHausses(data.hausses);
        setBaisses(data.baisses);
      } catch (error) {
        console.error('Erreur:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchMovers();
  }, []);

  if (loading) return <div>Chargement...</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Top Hausses */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="text-green-600" />
          <h3 className="text-lg font-bold">Plus Fortes Hausses</h3>
        </div>
        <div className="space-y-3">
          {hausses.map((stock) => (
            <div key={stock.Symbole} className="flex items-center justify-between p-3 bg-green-50 rounded">
              <div>
                <div className="font-bold text-gray-900">{stock.Symbole}</div>
                <div className="text-sm text-gray-600">${stock.Prix.toFixed(2)}</div>
              </div>
              <div className="text-right">
                <div className="text-green-600 font-bold">+{stock.Variation_PCT.toFixed(2)}%</div>
                <div className="text-xs text-gray-500">{(stock.Volume / 1000000).toFixed(1)}M vol.</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Baisses */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingDown className="text-red-600" />
          <h3 className="text-lg font-bold">Plus Fortes Baisses</h3>
        </div>
        <div className="space-y-3">
          {baisses.map((stock) => (
            <div key={stock.Symbole} className="flex items-center justify-between p-3 bg-red-50 rounded">
              <div>
                <div className="font-bold text-gray-900">{stock.Symbole}</div>
                <div className="text-sm text-gray-600">${stock.Prix.toFixed(2)}</div>
              </div>
              <div className="text-right">
                <div className="text-red-600 font-bold">{stock.Variation_PCT.toFixed(2)}%</div>
                <div className="text-xs text-gray-500">{(stock.Volume / 1000000).toFixed(1)}M vol.</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}