'use client';

import { useState } from 'react';
import PredictionsOverview from '@/components/predictions/PredictionsOverview';
import StockSelector from '@/components/predictions/StockSelector';
import PredictionChart from '@/components/predictions/PredictionChart';

export default function PredictionsPage() {
  const [selectedStock, setSelectedStock] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Prédictions ML
          </h1>
          <p className="text-gray-600">
            Prédictions de prix basées sur Machine Learning (Prophet)
          </p>
          <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              🤖 <strong>Modèle :</strong> Facebook Prophet - Séries temporelles avec saisonnalité
            </p>
          </div>
        </div>

        {/* Vue d'ensemble */}
        <PredictionsOverview />

        {/* Grille : Sélecteur + Graphique */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Colonne gauche : Sélecteur */}
          <div className="lg:col-span-1">
            <StockSelector
              onSelectStock={setSelectedStock}
              selectedStock={selectedStock}
            />
          </div>

          {/* Colonne droite : Graphique */}
          <div className="lg:col-span-2">
            {selectedStock ? (
              <PredictionChart symbole={selectedStock} />
            ) : (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <div className="text-6xl mb-4">📈</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Sélectionnez une action
                </h3>
                <p className="text-gray-600">
                  Choisissez une action dans la liste pour voir les prédictions
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}