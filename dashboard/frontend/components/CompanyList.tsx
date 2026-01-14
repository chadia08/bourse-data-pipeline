'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Search } from 'lucide-react';
import { fetchCompanies } from '@/lib/api';

// Since this is a client component, we can't use server actions directly in the same way 
// inside useEffect without some setup, but here we can import the server function 
// if it's not 'use server' specific, or just fetch via an internal API route.
// Ideally, we pass initial data and filter client side OR use a transition.
// For simplicity in this structure, we will fetch on change.

export default function CompanyList({ initialCompanies, sectors }: { initialCompanies: any[], sectors: string[] }) {
    const [companies, setCompanies] = useState(initialCompanies);
    const [search, setSearch] = useState('');
    const [sector, setSector] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                // Determine if we should use the API directly or the wrapper.
                // Since `fetchCompanies` in lib/api.ts is an async function that calls the backend,
                // we can just call it. Next.js 13+ handles this gracefully.
                const data = await fetchCompanies(sector, search);
                setCompanies(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        const timeout = setTimeout(load, 300); // Debounce
        return () => clearTimeout(timeout);
    }, [search, sector]);

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                    <input
                        type="text"
                        placeholder="Rechercher une société..."
                        className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
                <select
                    className="border border-slate-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary bg-white"
                    value={sector}
                    onChange={(e) => setSector(e.target.value)}
                >
                    <option value="">Tous les secteurs</option>
                    {sectors.map(s => (
                        <option key={s} value={s}>{s}</option>
                    ))}
                </select>
            </div>

            <div className={`bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden ${loading ? 'opacity-50' : ''}`}>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-slate-500 uppercase bg-slate-50">
                            <tr>
                                <th className="px-6 py-3">Symbole</th>
                                <th className="px-6 py-3">Nom</th>
                                <th className="px-6 py-3">Secteur</th>
                                <th className="px-6 py-3 text-right">Cours</th>
                                <th className="px-6 py-3 text-right">Var %</th>
                                <th className="px-6 py-3 text-right">Volume</th>
                            </tr>
                        </thead>
                        <tbody>
                            {companies.length > 0 ? (
                                companies.map((company: any) => {
                                    // Conversion sécurisée en nombre pour éviter les crashs
                                    const prix = company.prix_cloture ? Number(company.prix_cloture) : null;
                                    const variation = company.variation ? Number(company.variation) : 0;
                                    const volume = company.volume ? Number(company.volume) : 0;

                                    return (
                                        <tr key={company.symbole} className="border-b hover:bg-slate-50 transition-colors">
                                            <td className="px-6 py-4 font-mono font-medium text-accent">
                                                <Link href={`/company/${company.symbole}`}>
                                                    {company.symbole}
                                                </Link>
                                            </td>
                                            <td className="px-6 py-4 font-medium text-slate-900">
                                                <Link href={`/company/${company.symbole}`}>
                                                    {company.nom}
                                                </Link>
                                            </td>
                                            <td className="px-6 py-4 text-slate-500">
                                                {company.secteur}
                                            </td>
                                            <td className="px-6 py-4 text-right font-medium">
                                                {prix !== null ? `${prix.toFixed(2)} MAD` : '-'}
                                            </td>
                                            <td className={`px-6 py-4 text-right font-medium ${
                                                variation > 0 ? 'text-green-600' : 
                                                variation < 0 ? 'text-red-600' : 'text-slate-500'
                                            }`}>
                                                {variation > 0 ? '+' : ''}{variation.toFixed(2)}%
                                            </td>
                                            <td className="px-6 py-4 text-right text-slate-600">
                                                {volume > 0 ? volume.toLocaleString('fr-FR') : '-'}
                                            </td>
                                        </tr>
                                    );
                                })
                            ) : (
                                <tr>
                                    <td colSpan={6} className="px-6 py-8 text-center text-slate-500">
                                        {loading ? 'Chargement...' : 'Aucune société trouvée.'}
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
