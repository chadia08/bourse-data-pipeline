'use client';

import { useEffect, useState } from 'react';
import { getPredictionsList } from '@/lib/api';
import { Search } from 'lucide-react';

interface Stock {
  symbole: string;
  nom: string;
  secteur: string;
  nb_points: number;
  dernier_prix: number;
}

interface StockSelectorProps {
  onSelectStock: (symbole: string) => void;
  selectedStock: string | null;
}

export default function StockSelector({ onSelectStock, selectedStock }: StockSelectorProps) {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStocks() {
      try {
        const data = await getPredictionsList();
        setStocks(data);
      } catch (error) {
        console.error('Erreur:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchStocks();
  }, []);

  const filteredStocks = stocks.filter(
    (stock) =>
      stock.symbole.toLowerCase().includes(search.toLowerCase()) ||
      stock.nom.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return <div className="bg-white rounded-lg shadow p-6">Chargement...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h3 className="text-lg font-bold mb-4">Sélectionner une action</h3>
        <div className="relative">
          <Search className="absolute left-3 top-3 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Rechercher par symbole ou nom..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="max-h-96 overflow-y-auto">
        {filteredStocks.map((stock) => (
          <button
            key={stock.symbole}
            onClick={() => onSelectStock(stock.symbole)}
            className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition border-b ${
              selectedStock === stock.symbole ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="font-bold text-gray-900">{stock.symbole}</div>
                <div className="text-sm text-gray-600">{stock.nom}</div>
                <div className="text-xs text-gray-500">{stock.secteur}</div>
              </div>
              <div className="text-right">
                <div className="font-medium text-gray-900">${stock.dernier_prix.toFixed(2)}</div>
                <div className="text-xs text-gray-500">{stock.nb_points} pts</div>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}