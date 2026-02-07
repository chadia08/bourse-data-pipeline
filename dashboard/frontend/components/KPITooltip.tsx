'use client';

import { useState, useRef, useEffect } from 'react';
import { kpiExplanations, GENERAL_DISCLAIMER } from '@/lib/kpiExplanations';

interface KPITooltipProps {
  kpiKey: string;
  showDisclaimer?: boolean;
}

export default function KPITooltip({ kpiKey, showDisclaimer = false }: KPITooltipProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState<'left' | 'right'>('left');
  const buttonRef = useRef<HTMLButtonElement>(null);
  const explanation = kpiExplanations[kpiKey];

  useEffect(() => {
    if (isOpen && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      const spaceOnRight = window.innerWidth - rect.right;
      
      // Si moins de 420px à droite, afficher à gauche
      if (spaceOnRight < 420) {
        setPosition('right');
      } else {
        setPosition('left');
      }
    }
  }, [isOpen]);

  if (!explanation) return null;

  return (
    <div className="relative inline-block ml-1">
      {/* Icône ? */}
      <button
        ref={buttonRef}
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-blue-600 bg-blue-100 rounded-full hover:bg-blue-200 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-label="Plus d'informations"
      >
        ?
      </button>

      {/* Popup */}
      {isOpen && (
        <>
          {/* Overlay pour fermer en cliquant ailleurs */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Contenu du popup avec positionnement intelligent */}
          <div 
            className={`absolute top-8 z-50 w-96 max-w-[90vw] p-5 bg-white rounded-lg shadow-2xl border border-gray-200 max-h-[80vh] overflow-y-auto ${
              position === 'right' ? 'right-0' : 'left-0'
            }`}
            style={{
              // Si trop à droite de l'écran, forcer l'alignement
              ...(position === 'right' ? { transform: 'translateX(0)' } : {})
            }}
          >
            {/* En-tête */}
            <div className="flex items-start justify-between mb-3">
              <h3 className="text-lg font-bold text-gray-900">
                {explanation.title}
              </h3>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
              >
                ×
              </button>
            </div>

            {/* Description */}
            <p className="text-sm text-gray-700 mb-4 leading-relaxed">
              {explanation.description}
            </p>

            {/* Interprétation */}
            <div className="mb-4 p-3 bg-gray-50 rounded-md">
              <p className="text-xs font-semibold text-gray-600 mb-2">
                Comment l'interpréter :
              </p>
              <ul className="space-y-1 text-xs text-gray-700">
                <li>{explanation.interpretation.good}</li>
                {explanation.interpretation.neutral && (
                  <li>{explanation.interpretation.neutral}</li>
                )}
                <li>{explanation.interpretation.bad}</li>
              </ul>
            </div>

            {/* Exemple */}
            <div className="mb-4 p-3 bg-blue-50 rounded-md border-l-4 border-blue-500">
              <p className="text-xs font-semibold text-blue-900 mb-1">
                💡 Exemple concret :
              </p>
              <p className="text-xs text-blue-800">
                {explanation.example}
              </p>
            </div>

            {/* Disclaimer */}
            <div className="pt-3 border-t border-gray-200">
              <p className="text-xs text-amber-700 bg-amber-50 p-2 rounded-md border border-amber-200">
                ⚠️ {explanation.disclaimer}
              </p>
            </div>

            {/* Disclaimer général (optionnel) */}
            {showDisclaimer && (
              <div className="mt-4 pt-3 border-t border-gray-300">
                <details className="text-xs text-gray-600">
                  <summary className="cursor-pointer font-semibold text-red-600 hover:text-red-700">
                    ⚠️ Avertissement Important
                  </summary>
                  <div className="mt-2 pl-4 text-gray-700 whitespace-pre-line">
                    {GENERAL_DISCLAIMER}
                  </div>
                </details>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}