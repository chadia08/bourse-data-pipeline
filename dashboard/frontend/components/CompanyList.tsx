'use client';
import { useState } from 'react';
import Link from 'next/link';
import { Search, ShieldCheck, TrendingUp, AlertCircle } from 'lucide-react';

export default function CompanyList({ initialCompanies }: { initialCompanies: any[] }) {
    const [search, setSearch] = useState('');

    // Filtrage sur le symbole ou le nom (Identity.Nom du script 2)
    const filtered = initialCompanies.filter(c => 
        c.symbole.toLowerCase().includes(search.toLowerCase()) || 
        (c.nom && c.nom.toLowerCase().includes(search.toLowerCase()))
    );

    return (
        <div className="space-y-6">
            <div className="relative max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input 
                    className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none"
                    placeholder="Rechercher (ex: DAL, HRL...)"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
                <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-bold">
                        <tr>
                            <th className="px-6 py-4">Valeur</th>
                            <th className="px-6 py-4 text-right">Dernier Prix</th>
                            <th className="px-6 py-4 text-center">Santé IA</th>
                            <th className="px-6 py-4 text-center">Momentum (RSI)</th>
                            <th className="px-6 py-4 text-right">Performance 5J</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {filtered.map((company) => (
                            <tr key={company.symbole} className="hover:bg-slate-50 transition-colors">
                                <td className="px-6 py-4">
                                    <Link href={`/company/${company.symbole}`}>
                                        <div className="font-bold text-blue-600">{company.symbole}</div>
                                        <div className="text-[11px] text-slate-400 truncate max-w-[150px]">{company.nom}</div>
                                    </Link>
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <div className="font-bold">{company.prix?.toFixed(2)} MAD</div>
                                    <div className={`text-[11px] font-bold ${company.variation >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {company.variation >= 0 ? '+' : ''}{company.variation}%
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-center">
                                    <span className={`px-2 py-1 rounded-md text-[11px] font-bold flex items-center justify-center gap-1 mx-auto w-20 ${
                                        company.score > 60 ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                                    }`}>
                                        <ShieldCheck size={12} /> {company.score}/100
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-center">
                                    <div className={`text-[11px] font-medium ${company.rsi > 70 ? 'text-red-600' : company.rsi < 30 ? 'text-green-600' : 'text-slate-600'}`}>
                                        {company.rsi > 70 ? 'Suracheté' : company.rsi < 30 ? 'Survendu' : 'Neutre'}
                                        <div className="text-[9px] text-slate-400">RSI: {company.rsi?.toFixed(1)}</div>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-right font-mono font-bold text-slate-700">
                                    {company.perf5j > 0 ? '+' : ''}{company.perf5j?.toFixed(2)}%
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}