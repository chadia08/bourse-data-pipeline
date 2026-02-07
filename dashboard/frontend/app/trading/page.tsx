import TradingOverview from '@/components/trading/TradingOverview';
import SignalsTable from    '@/components/trading/SignalsTable';
import TopMovers from '@/components/trading/TopMovers';
import KPITooltip from '@/components/KPITooltip';

export default function TradingPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Trading</h1>
          <p className="text-gray-600">Analyse technique et signaux en temps réel</p>
        </div>

        {/* Vue d'ensemble */}
        <TradingOverview />

        {/* Table des signaux */}
        <div className="mb-8">
          <SignalsTable />
        </div>

        {/* Top Movers */}
        <TopMovers />
      </div>
    </div>
  );
}