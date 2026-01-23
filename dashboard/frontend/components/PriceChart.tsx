'use client';

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface PricePoint {
  date: string;
  prix_cloture: number;
}

export default function PriceChart({ data }: { data: PricePoint[] }) {
  if (!data || data.length === 0) return <div className="h-[300px] flex items-center justify-center text-slate-400">Pas de données graphiques</div>;

  const formattedData = data.map(d => ({
    ...d,
    date: new Date(d.date).toLocaleDateString('fr-MA')
  }));

  return (
    <div className="h-[400px] w-full bg-white p-4 rounded-xl border border-slate-100">
      <h3 className="text-lg font-semibold mb-4">Évolution du cours</h3>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={formattedData}
          margin={{
            top: 10,
            right: 30,
            left: 0,
            bottom: 0,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="date" tick={{fontSize: 12}} />
          <YAxis domain={['auto', 'auto']} tick={{fontSize: 12}} />
          <Tooltip />
          <Area type="monotone" dataKey="prix_cloture" stroke="#3b82f6" fill="#eff6ff" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
