// app/company/[symbol]/page.tsx
'use client';
import { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Activity, ShieldCheck, TrendingUp, DollarSign } from 'lucide-react';

export default function CompanyDetail({ params }: { params: { symbol: string } }) {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    // On récupère les données fusionnées pour ce symbole
    fetch(`https://refactored-acorn-wrpww7j7q79jhv996-3000.app.github.dev/api/stocks/prices`)
      .then(res => res.json())
      .then(allStocks => {
        const company = allStocks.find((s: any) => s.symbole === params.symbol);
        setData(company);
      });
  }, [params.symbol]);

  if (!data) return <div className="p-10 text-center">Chargement des données de {params.symbol}...</div>;

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8 bg-slate-50 min-h-screen">
      
      {/* HEADER : Identité et Prix Live */}
      <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-black text-slate-900">{data.nom}</h1>
          <p className="text-slate-500 font-bold uppercase tracking-widest mt-1">
            {data.symbole} • {data.secteur || 'Secteur N/A'}
          </p>
        </div>
        <div className="text-right">
          <div className="text-4xl font-mono font-bold text-slate-900">{data.prix?.toFixed(2)} MAD</div>
          <div className={`font-bold ${data.variation >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {data.variation >= 0 ? '▲' : '▼'} {data.variation}%
          </div>
        </div>
        {/* SECTION DESCRIPTION GEMINI */}
        <div className="bg-gradient-to-br from-blue-50 to-white p-6 rounded-3xl border border-blue-100 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                <h3 className="text-xs font-black text-blue-900 uppercase tracking-widest">Analyse de l'activité (IA)</h3>
            </div>
            <p className="text-slate-700 leading-relaxed text-lg italic">
                "{data.description}"
            </p>
        </div>
      </div>

      {/* KPI GRID : Valorisation & Santé */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard title="EPS (Bénéfice/Action)" value={`${data.eps || '0.00'}`} sub="Dernier annuel" icon={<DollarSign className="text-blue-500" />} />
        <StatCard title="P/E Ratio" value={data.eps > 0 ? (data.prix / data.eps).toFixed(2) : 'N/A'} sub="Valorisation" icon={<Activity className="text-purple-500" />} />
        <StatCard title="Score Solidité IA" value={`${data.score}/100`} sub="Analyse Algorithmique" icon={<ShieldCheck className="text-emerald-500" />} />
        <StatCard title="RSI (Momentum)" value={data.rsi?.toFixed(2)} sub={data.rsi > 70 ? 'Suracheté' : 'Neutre'} icon={<TrendingUp className="text-orange-500" />} />
      </div>

      {/* GRAPHIQUES : Évolution Financière */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Graphique du Revenu vs Profit */}
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
          <h3 className="text-lg font-bold mb-6 text-slate-800">Historique des Revenus & Profits</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.historique}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="annee" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="revenu" name="Chiffre d'Affaires" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="profit" name="Résultat Net" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Graphique de la Rentabilité (ROE) */}
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
          <h3 className="text-lg font-bold mb-6 text-slate-800">Évolution de la Rentabilité (ROE %)</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.historique}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="annee" />
                <YAxis unit="%" />
                <Tooltip />
                <Line type="monotone" dataKey="roe" stroke="#f59e0b" strokeWidth={4} dot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, sub, icon }: any) {
  return (
    <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
      <div className="flex justify-between items-start mb-4">
        <div className="p-2 bg-slate-50 rounded-xl">{icon}</div>
      </div>
      <div className="text-sm font-bold text-slate-400 uppercase tracking-wider">{title}</div>
      <div className="text-2xl font-black text-slate-900 mt-1">{value}</div>
      <div className="text-xs font-bold text-slate-500 mt-2">{sub}</div>
    </div>
  );
}