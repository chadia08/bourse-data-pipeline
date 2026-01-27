// app/page.tsx
import Link from 'next/link';
import { ArrowUpRight, ArrowDownRight, Activity } from 'lucide-react';

async function getStocksData() {
  try {
    // Utilisation de votre URL Codespaces publique
    const baseUrl = "https://refactored-acorn-wrpww7j7q79jhv996-3000.app.github.dev";
    const res = await fetch(`${baseUrl}/api/stocks/prices`, { 
      cache: 'no-store',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (!res.ok) return [];
    return res.json();
  } catch (error) {
    console.error("Erreur lors de la récupération des données:", error);
    return [];
  }
}

export default async function Home() {
  // Récupération des données depuis l'API fusionnée
  const stocks = await getStocksData();

  // Filtrage de sécurité : on ne garde que les objets ayant une clé 'prix'
  const validStocks = stocks.filter((s: any) => s && s.prix !== undefined);

  // Tri pour les "Tops Performances" basé sur la clé 'variation'
  const gainers = [...validStocks]
    .sort((a, b) => (b.variation || 0) - (a.variation || 0))
    .slice(0, 5);

  // Tri pour les "Alertes Baisses" basé sur la clé 'variation'
  const losers = [...validStocks]
    .sort((a, b) => (a.variation || 0) - (b.variation || 0))
    .slice(0, 5);

  // Calcul de la moyenne du marché
  const marketAvg = validStocks.length > 0 
    ? (validStocks.reduce((acc: number, curr: any) => acc + (curr.variation || 0), 0) / validStocks.length).toFixed(2)
    : "0.00";

  return (
    <div className="p-8 space-y-8 bg-slate-50 min-h-screen">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Tableau de Bord IA</h1>
          <p className="text-slate-500 font-medium">Données réelles : {validStocks.length} actions détectées</p>
        </div>
        <div className="bg-green-100 text-green-700 px-4 py-2 rounded-full flex items-center gap-2 text-sm font-bold shadow-sm">
          <Activity size={16} /> MARCHÉ OUVERT
        </div>
      </header>

      {/* Cartes de synthèse (KPIs) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Actions Suivies</h3>
          <p className="text-4xl font-black text-slate-900 mt-2">{validStocks.length}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Moyenne du Marché</h3>
          <p className={`text-4xl font-black mt-2 ${Number(marketAvg) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
             {marketAvg}%
          </p>
        </div>
      </div>

      {/* Grille des Movers (Hausses et Baisses) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Section Tops Performances */}
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-green-600">
            <ArrowUpRight strokeWidth={3} /> Tops Performances
          </h2>
          <div className="space-y-3">
            {gainers.map((stock: any) => (
              <Link href={`/company/${stock.symbole}`} key={stock.symbole} 
                    className="flex justify-between items-center p-4 hover:bg-slate-50 rounded-2xl transition border border-transparent hover:border-slate-100">
                <div>
                  <div className="font-bold text-slate-800 text-lg">{stock.symbole}</div>
                  <div className="text-xs text-slate-400 font-medium">{stock.nom || 'N/A'}</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-slate-900">{stock.prix?.toFixed(2)} MAD</div>
                  <div className="text-green-500 font-black">+{stock.variation}%</div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Section Alertes Baisses */}
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
          <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-red-600">
            <ArrowDownRight strokeWidth={3} /> Alertes Baisses
          </h2>
          <div className="space-y-3">
            {losers.map((stock: any) => (
              <Link href={`/company/${stock.symbole}`} key={stock.symbole} 
                    className="flex justify-between items-center p-4 hover:bg-slate-50 rounded-2xl transition border border-transparent hover:border-slate-100">
                <div>
                  <div className="font-bold text-slate-800 text-lg">{stock.symbole}</div>
                  <div className="text-xs text-slate-400 font-medium">{stock.nom || 'N/A'}</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-slate-900">{stock.prix?.toFixed(2)} MAD</div>
                  <div className="text-red-500 font-black">{stock.variation}%</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}