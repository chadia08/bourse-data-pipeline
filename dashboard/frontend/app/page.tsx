// app/page.tsx
import Link from 'next/link';
import { ArrowUpRight, ArrowDownRight, Activity, Building2 } from 'lucide-react';

async function getStocksData() {
  // L'URL exacte qui fonctionne dans ton navigateur
  const baseUrl = "http://localhost:3000";
  
  try {
    const res = await fetch(`${baseUrl}/api/stocks/prices`, { 
      cache: 'no-store',
      headers: { 'Accept': 'application/json' }
    });
    
    if (!res.ok) return [];

    const data = await res.json();
    return Array.isArray(data) ? data : [];
  } catch (error) {
    console.error("Erreur de fetch:", error);
    return [];
  }
}

export default async function Home() {
  const stocks = await getStocksData();

  // On valide les stocks sur la base des clés 'symbole' et 'prix'
  const validStocks = stocks.filter((s: any) => s && s.symbole && s.prix !== undefined);

  const gainers = [...validStocks]
    .sort((a: any, b: any) => (b.variation || 0) - (a.variation || 0))
    .slice(0, 5);

  const losers = [...validStocks]
    .sort((a: any, b: any) => (a.variation || 0) - (b.variation || 0))
    .slice(0, 5);

  const marketAvg = validStocks.length > 0 
    ? (validStocks.reduce((acc: number, curr: any) => acc + (curr.variation || 0), 0) / validStocks.length).toFixed(2)
    : "0.00";

  return (
    <div className="p-8 space-y-8 bg-slate-50 min-h-screen">
      {/* Header */}
      <header className="flex justify-between items-center bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">
            MarketData <span className="text-blue-600">Intelligence</span>
          </h1>
          <p className="text-slate-500 font-medium">Suivi de {validStocks.length} actifs en temps réel</p>
        </div>
        <div className="bg-emerald-50 text-emerald-600 px-4 py-2 rounded-full flex items-center gap-2 text-sm font-bold border border-emerald-100">
          <Activity size={16} /> MARCHÉ OUVERT
        </div>
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">Couverture Marché</p>
          <p className="text-5xl font-black text-slate-900 mt-2">{validStocks.length}</p>
        </div>
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">Indice de Tendance</p>
          <p className={`text-5xl font-black mt-2 ${Number(marketAvg) >= 0 ? 'text-emerald-500' : 'text-red-500'}`}>
             {marketAvg}%
          </p>
        </div>
      </div>

      {/* Listes de Performances */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Tops Performances */}
        <div className="space-y-4">
          <h2 className="text-xl font-black text-slate-800 flex items-center gap-2 px-2 text-emerald-600">
            <ArrowUpRight size={20} strokeWidth={3} /> Tops Performances
          </h2>
          <div className="grid gap-3">
            {gainers.map((stock: any) => (
              <Link href={`/company/${stock.symbole}`} key={stock.symbole} 
                    className="group bg-white p-4 rounded-2xl flex justify-between items-center border border-slate-100 hover:border-emerald-200 transition-all">
                <div className="flex items-center gap-4">
                  <div className="font-black text-slate-900">{stock.nom || stock.symbole}</div>
                </div>
                <div className="text-right">
                  <div className="font-mono font-bold text-slate-900">{stock.prix?.toFixed(2)} MAD</div>
                  <div className="text-emerald-500 font-black">+{stock.variation}%</div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Alertes Baisses */}
        <div className="space-y-4">
          <h2 className="text-xl font-black text-slate-800 flex items-center gap-2 px-2 text-red-600">
            <ArrowDownRight size={20} strokeWidth={3} /> Alertes Baisses
          </h2>
          <div className="grid gap-3">
            {losers.map((stock: any) => (
              <Link href={`/company/${stock.symbole}`} key={stock.symbole} 
                    className="group bg-white p-4 rounded-2xl flex justify-between items-center border border-slate-100 hover:border-red-200 transition-all">
                <div className="flex items-center gap-4">
                  <div className="font-black text-slate-900">{stock.nom || stock.symbole}</div>
                </div>
                <div className="text-right">
                  <div className="font-mono font-bold text-slate-900">{stock.prix?.toFixed(2)} MAD</div>
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