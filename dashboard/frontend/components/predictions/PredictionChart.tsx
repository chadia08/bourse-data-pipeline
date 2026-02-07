'use client';

import { useEffect, useState } from 'react';
import { getPredictionHistory, getForecast } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart } from 'recharts';
import { TrendingUp, TrendingDown, Loader2 } from 'lucide-react';

interface PredictionChartProps {
  symbole: string;
}

export default function PredictionChart({ symbole }: PredictionChartProps) {
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState<any[]>([]);
  const [tendance, setTendance] = useState<any>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        // Récupérer historique et prédictions
        const [historyData, forecastData] = await Promise.all([
          getPredictionHistory(symbole, 60),
          getForecast(symbole, 30),
        ]);

        // Combiner les données pour le graphique
        const combined = [
          ...historyData.history.map((h: any) => ({
            date: h.date,
            prix_reel: h.price,
            type: 'historique',
          })),
          ...forecastData.predictions.map((p: any) => ({
            date: p.date,
            prix_predit: p.predicted_price,
            lower: p.lower_bound,
            upper: p.upper_bound,
            type: 'prediction',
          })),
        ];

        setChartData(combined);
        setTendance(forecastData.tendance);
      } catch (error) {
        console.error('Erreur:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [symbole]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Génération des prédictions...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-gray-900">{symbole}</h3>
            <p className="text-sm text-gray-600">Prédictions sur 30 jours</p>
          </div>
          {tendance && (
            <div className="text-right">
              <div className="flex items-center gap-2">
                {tendance.direction === 'Haussière' ? (
                  <TrendingUp className="text-green-600 w-6 h-6" />
                ) : (
                  <TrendingDown className="text-red-600 w-6 h-6" />
                )}
                <span
                  className={`text-2xl font-bold ${
                    tendance.variation_pct > 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {tendance.variation_pct > 0 ? '+' : ''}
                  {tendance.variation_pct.toFixed(2)}%
                </span>
              </div>
              <p className="text-sm text-gray-600">{tendance.direction}</p>
            </div>
          )}
        </div>
      </div>

      <div className="p-6">
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => {
                const date = new Date(value);
                return `${date.getMonth() + 1}/${date.getDate()}`;
              }}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
              formatter={(value: any) => `$${value?.toFixed(2)}`}
            />
            <Legend />
            
            {/* Prix réel */}
            <Line
              type="monotone"
              dataKey="prix_reel"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
              name="Prix Réel"
            />
            
            {/* Prix prédit */}
            <Line
              type="monotone"
              dataKey="prix_predit"
              stroke="#f59e0b"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="Prédiction"
            />
            
            {/* Intervalle de confiance */}
            <Area
              type="monotone"
              dataKey="upper"
              stroke="none"
              fill="#f59e0b"
              fillOpacity={0.1}
              name="Borne Supérieure"
            />
            <Area
              type="monotone"
              dataKey="lower"
              stroke="none"
              fill="#f59e0b"
              fillOpacity={0.1}
              name="Borne Inférieure"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {tendance && (
        <div className="p-6 border-t bg-gray-50">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Prix Initial (prédit)</p>
              <p className="text-lg font-bold text-gray-900">${tendance.prix_initial.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Prix Final (prédit)</p>
              <p className="text-lg font-bold text-gray-900">${tendance.prix_final.toFixed(2)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}