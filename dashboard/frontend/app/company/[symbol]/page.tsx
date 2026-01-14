import { fetchCompanyDetails, fetchChartData } from '@/lib/api';
import PriceChart from '@/components/PriceChart';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default async function CompanyPage({ params }: { params: { symbol: string } }) {
  const { symbol } = params;
  console.log(`[Server] Fetching details for symbol: ${symbol}`);
  const data = await fetchCompanyDetails(symbol);
  console.log(`[Server] Data received:`, data);
  const chartData = await fetchChartData(symbol);

  if (!data) {
      console.error(`[Server] No data for ${symbol}`);
      return <div className="p-6 text-red-600">Erreur: Impossible de charger les données pour {symbol}</div>
  }
  
  if (!data.fundamentals) {
      console.error(`[Server] No fundamentals for ${symbol}`, data);
      return <div className="p-6 text-red-600">Erreur: Pas de données fondamentales pour {symbol}</div>
  }

  const { fundamentals: f, latest_price: p } = data;

  return (
    <div className="space-y-6">
        <Link href="/" className="inline-flex items-center text-sm text-slate-500 hover:text-primary mb-4">
            <ArrowLeft className="w-4 h-4 mr-1" /> Retour au marché
        </Link>
        
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">{f.nom}</h1>
                    <div className="flex items-center gap-2 mt-2 text-slate-500">
                        <span className="font-mono bg-slate-100 px-2 py-1 rounded text-xs">{symbol}</span>
                        <span>•</span>
                        <span>{f.secteur}</span>
                        <span>•</span>
                        <span>{f.sous_secteur}</span>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-3xl font-bold">{p?.prix_cloture?.toFixed(2)} MAD</div>
                    {p?.variation && (
                        <div className={`font-medium ${p.variation >= 0 ? 'text-success' : 'text-danger'}`}>
                            {p.variation > 0 ? '+' : ''}{p.variation.toFixed(2)}%
                        </div>
                    )}
                </div>
            </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
                <PriceChart data={chartData} />
                
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-semibold mb-4">Fondamentaux</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-6">
                        <div>
                            <div className="text-xs text-slate-500 uppercase">Revenu Total</div>
                            <div className="font-semibold">{f.revenu_total && f.revenu_total > 0 ? Number(f.revenu_total).toLocaleString('fr-FR') : 'N/A'} MAD</div>
                        </div>
                        <div>
                            <div className="text-xs text-slate-500 uppercase">Résultat Net</div>
                            <div className="font-semibold">{f.resultat_net && f.resultat_net > 0 ? Number(f.resultat_net).toLocaleString('fr-FR') : 'N/A'} MAD</div>
                        </div>
                         <div>
                            <div className="text-xs text-slate-500 uppercase">Total Actifs</div>
                            <div className="font-semibold">{f.total_actifs && f.total_actifs > 0 ? Number(f.total_actifs).toLocaleString('fr-FR') : 'N/A'} MAD</div>
                        </div>
                        <div>
                            <div className="text-xs text-slate-500 uppercase">Marge Nette</div>
                            <div className="font-semibold">{f.marge_beneficiaire ? (Number(f.marge_beneficiaire) * 100).toFixed(2) : 'N/A'}%</div>
                        </div>
                         <div>
                            <div className="text-xs text-slate-500 uppercase">ROE</div>
                            <div className="font-semibold">{f.rentabilite_fonds_propres_roe ? (Number(f.rentabilite_fonds_propres_roe) * 100).toFixed(2) : 'N/A'}%</div>
                        </div>
                         <div>
                            <div className="text-xs text-slate-500 uppercase">Ratio Courant</div>
                            <div className="font-semibold">{f.ratio_courant ? Number(f.ratio_courant).toFixed(2) : 'N/A'}</div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="space-y-6">
                 <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-semibold mb-4">Informations</h3>
                    <ul className="space-y-2 text-sm">
                        <li className="flex justify-between">
                            <span className="text-slate-500">Secteur</span>
                            <span className="font-medium">{f.secteur || 'N/A'}</span>
                        </li>
                        <li className="flex justify-between">
                            <span className="text-slate-500">Sous-secteur</span>
                            <span className="font-medium">{f.sous_secteur || 'N/A'}</span>
                        </li>
                        {f.siege && (
                            <li className="flex justify-between">
                                <span className="text-slate-500">Siège</span>
                                <span className="font-medium text-right">{f.siege}</span>
                            </li>
                        )}
                        {f.date_introduction && (
                            <li className="flex justify-between">
                                <span className="text-slate-500">IPO</span>
                                <span className="font-medium">{new Date(f.date_introduction).toLocaleDateString('fr-FR')}</span>
                            </li>
                        )}
                    </ul>
                 </div>
                 
                 <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-semibold mb-4">Données du Jour</h3>
                    <ul className="space-y-3 text-sm">
                         <li className="flex justify-between">
                            <span className="text-slate-500">Volume</span>
                            <span className="font-medium">{p?.volume ? Number(p.volume).toLocaleString('fr-FR') : 'N/A'}</span>
                        </li>
                        <li className="flex justify-between">
                            <span className="text-slate-500">Date</span>
                            <span className="font-medium">{p?.date ? new Date(p.date).toLocaleDateString('fr-FR') : 'N/A'}</span>
                        </li>
                    </ul>
                 </div>
            </div>
        </div>
    </div>
  )
}
