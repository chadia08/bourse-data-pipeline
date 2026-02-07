'use client';
import { useState, useEffect } from 'react';
import CompanyList from '@/components/CompanyList';

export default function CompaniesPage() {
  const [stocks, setStocks] = useState([]);
  const [selectedYears, setSelectedYears] = useState<number[]>([]);

  useEffect(() => {
    // Appel à ton API de fusion (qui contient maintenant l'historique)
    fetch('http://localhost:3000/api/stocks/prices')
      .then(res => res.json())
      .then(data => {
        setStocks(data);
        // Par défaut, on peut sélectionner l'année la plus récente
        const allYears = Array.from(new Set(data.flatMap((s: any) => s.annees_disponibles || [])));
        if (allYears.length > 0) setSelectedYears([Math.max(...allYears as number[])]);
      });
  }, []);

  // 1. Extraction DYNAMIQUE des années (le code que tu as demandé)
  const allPossibleYears = Array.from(new Set(stocks.flatMap((s: any) => s.annees_disponibles || [])))
  .filter((year: any) => year > 2000 && year < 2100) 
  .sort((a: any, b: any) => b - a);
  
  return (
    <div className="p-8 space-y-6">
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <h2 className="text-sm font-bold text-slate-400 uppercase mb-4 tracking-wider">
          Filtrer par Années Fiscales (Dynamique)
        </h2>
        
        {/* 2. Affichage des cases à cocher */}
        <div className="flex flex-wrap gap-6">
          {allPossibleYears.map((year: any) => (
            <label key={year} className="flex items-center gap-2 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={selectedYears.includes(year)}
                onChange={(e) => {
                  if (e.target.checked) setSelectedYears([...selectedYears, year]);
                  else setSelectedYears(selectedYears.filter(y => y !== year));
                }}
                className="w-5 h-5 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-slate-700 font-semibold group-hover:text-blue-600 transition-colors">
                {year}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* 3. Ton tableau ou tes graphiques en dessous */}
      <CompanyList initialCompanies={stocks} />
    </div>
  );
}