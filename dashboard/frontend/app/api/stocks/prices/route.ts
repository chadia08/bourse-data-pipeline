// dashboard/frontend/app/api/stocks/prices/route.ts
import { MongoClient } from 'mongodb';
import { NextResponse } from 'next/server';

export async function GET() {
  const uri = "mongodb://localhost:27017";
  const client = new MongoClient(uri);

  try {
    await client.connect();
    const db = client.db('bourse_cache');
    // On récupère les données de la collection kpi_prices
    const data = await db.collection('kpi_prices').find({}).toArray();
    
    return NextResponse.json(data);
  } catch (e) {
    return NextResponse.json({ error: "Fail" }, { status: 500 });
  } finally {
    await client.close();
  }
}