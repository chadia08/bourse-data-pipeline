import InvestmentOverview from '@/components/investment/InvestmentOverview';
import InvestmentScreener from '@/components/investment/InvestmentScreener';
import KPITooltip from '@/components/KPITooltip';

export default function InvestmentPage() {
  return (
    <div className="min-h-screen bg-gray-50 px-4 py-6">
      <div className="max-w-[1600px] mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Investissement</h1>
          <p className="text-gray-600">Analyse fondamentale et sélection d'actions long terme</p>
        </div>

        {/* Vue d'ensemble */}
        <InvestmentOverview />

        {/* Screener */}
        <InvestmentScreener />
      </div>
    </div>
  );
}