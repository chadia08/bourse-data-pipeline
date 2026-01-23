import { fetchMarketStatus, fetchTopMovers } from '@/lib/api';
import Link from 'next/link';

export default async function Home() {
  const status = await fetchMarketStatus();
  const movers = await fetchTopMovers();

  return (
    <div className="space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Vue d'ensemble du marché</h1>
        <p className="text-slate-500">Données en temps réel de ClickHouse</p>
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
          <h3 className="text-sm font-medium text-slate-500">Volume Quotidien</h3>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            {status?.volume ? status.volume.toLocaleString() : '-'}
          </p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
            <h3 className="text-sm font-medium text-slate-500">Valeur Échangée (MAD)</h3>
            <p className="text-2xl font-bold text-slate-900 mt-2">
                {status?.value ? new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD' }).format(status.value) : '-'}
            </p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
            <h3 className="text-sm font-medium text-slate-500">État du Marché</h3>
            <span className={`inline-block mt-2 px-3 py-1 rounded-full text-sm font-medium ${status?.status === 'OPEN' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                {status?.status || 'Fermé'}
            </span>
        </div>
      </div>

      {/* Movers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50/50">
                <h2 className="font-semibold text-slate-900">Plus Fortes Hausses</h2>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="text-xs text-slate-500 uppercase bg-slate-50">
                        <tr>
                            <th className="px-4 py-3">Société</th>
                            <th className="px-4 py-3 text-right">Dernier</th>
                            <th className="px-4 py-3 text-right">Var %</th>
                        </tr>
                    </thead>
                    <tbody>
                        {movers?.gainers?.map((item: any) => (
                            <tr key={item.symbole} className="border-b hover:bg-slate-50">
                                <td className="px-4 py-3 font-medium text-slate-900">
                                    <Link href={`/company/${item.symbole}`} className="hover:text-accent">
                                        {item.nom || item.symbole}
                                    </Link>
                                </td>
                                <td className="px-4 py-3 text-right">{item.prix_cloture?.toFixed(2)}</td>
                                <td className="px-4 py-3 text-right text-success font-semibold">
                                    +{item.variation?.toFixed(2)}%
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
            <div className="p-4 border-b border-slate-100 bg-slate-50/50">
                <h2 className="font-semibold text-slate-900">Plus Fortes Baisses</h2>
            </div>
             <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="text-xs text-slate-500 uppercase bg-slate-50">
                         <tr>
                            <th className="px-4 py-3">Société</th>
                            <th className="px-4 py-3 text-right">Dernier</th>
                            <th className="px-4 py-3 text-right">Var %</th>
                        </tr>
                    </thead>
                    <tbody>
                         {movers?.losers?.map((item: any) => (
                            <tr key={item.symbole} className="border-b hover:bg-slate-50">
                                <td className="px-4 py-3 font-medium text-slate-900">
                                    <Link href={`/company/${item.symbole}`} className="hover:text-accent">
                                        {item.nom || item.symbole}
                                    </Link>
                                </td>
                                <td className="px-4 py-3 text-right">{item.prix_cloture?.toFixed(2)}</td>
                                <td className="px-4 py-3 text-right text-danger font-semibold">
                                    {item.variation?.toFixed(2)}%
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
      </div>
    </div>
  )
}
