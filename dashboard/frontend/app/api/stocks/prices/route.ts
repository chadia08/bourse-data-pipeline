import { MongoClient } from 'mongodb';
import { NextResponse } from 'next/server';

export async function GET() {
    const client = new MongoClient("mongodb://localhost:27017/");
    try {
        await client.connect();
        const db = client.db("bourse_cache");

        // Récupération simultanée des 4 sources de données
        const [prices, funds, momentum, invest, history] = await Promise.all([
            db.collection("kpi_prices").find().toArray(),
            db.collection("kpi_fundamentals").find().toArray(),
            db.collection("kpi_momentum").find().toArray(),
            db.collection("kpi_investment").find().toArray(),
            db.collection("kpi_history").find().toArray(),
        ]);

        const fullData = prices.map(p => {
            const f = funds.find(item => item.Symbole === p.Symbole);
            const m = momentum.find(item => item.Symbole === p.Symbole);
            const i = invest.find(item => item.Symbole === p.Symbole);
            const h = history.find(item => item.Symbole === p.Symbole);

            return {
                symbole: p.Symbole,
                nom: f?.Identity?.Nom || p.Symbole,
                secteur: f?.Identity?.Secteur || "N/A",
                prix: p.KPI_Prices?.Dernier_Prix,
                variation: p.KPI_Prices?.Variation_PCT,
                // Nouvelles colonnes issues de vos scripts 3 et 4
                rsi: m?.KPI_Momentum?.RSI_14J || 0,
                score: i?.KPI_Investment?.Score_Solidite_Financiere || 0,
                cagr: i?.KPI_Investment?.CAGR_Annualise_PCT || 0,
                description: h?.description || "Aucune description disponible.",
                historique: h?.Historique || [], // Liste dynamique des années fiscales
                annees_disponibles: h?.Historique.map((y: any) => y.annee) || []
            };
        });

        return NextResponse.json(fullData);
    } finally {
        await client.close();
    }
}