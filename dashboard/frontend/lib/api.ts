const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002/api';

export async function fetchMarketStatus(date?: string) {
  try {
    const query = date ? `?date=${date}` : '';
    const res = await fetch(`${API_URL}/market/status${query}`, { next: { revalidate: 30 } });
    if (!res.ok) throw new Error('Failed to fetch status');
    return res.json();
  } catch (e) {
    console.error(e);
    return null;
  }
}

export async function fetchTopMovers(date?: string, sector?: string) {
  const params = new URLSearchParams();
  if (date) params.append('date', date);
  if (sector && sector !== 'All') params.append('sector', sector);
    
  try {
    const res = await fetch(`${API_URL}/market/movers?${params.toString()}`, { next: { revalidate: 30 } });
    if (!res.ok) throw new Error('Failed to fetch movers');
    return res.json();
  } catch (e) {
    console.error(e);
    return null;
  }
}

export async function fetchCompanyDetails(symbol: string) {
    try {
        const res = await fetch(`${API_URL}/company/${symbol}`, { cache: 'no-store', next: { revalidate: 0 } });
        if (!res.ok) {
            console.error(`Failed to fetch company ${symbol}: ${res.status}`);
            return null;
        }
        const data = await res.json();
        console.log(`Company data for ${symbol}:`, data);
        return data;
    } catch (e) {
        console.error(`Error fetching company ${symbol}:`, e);
        return null;
    }
}

export async function fetchChartData(symbol: string, period: string = '1Y') {
    try {
        const res = await fetch(`${API_URL}/chart/${symbol}?period=${period}`, { cache: 'no-store' });
        if (!res.ok) throw new Error('Failed to fetch chart');
        return res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
}

export async function fetchCompanies(sector?: string, search?: string) {
    const params = new URLSearchParams();
    if (sector && sector !== 'All') params.append('sector', sector);
    if (search) params.append('search', search);

    try {
        const res = await fetch(`${API_URL}/companies?${params.toString()}`, { cache: 'no-store' });
        if (!res.ok) throw new Error('Failed to fetch companies');
        return res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
}

export async function fetchSectors() {
     try {
        const res = await fetch(`${API_URL}/sectors`, { next: { revalidate: 3600 } });
        if (!res.ok) throw new Error('Failed to fetch sectors');
        return res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================
// FONCTIONS EXISTANTES (gardez-les)
// ============================================================

// ... vos fonctions existantes ...

// ============================================================
// NOUVELLES FONCTIONS POUR TRADING
// ============================================================

// Vue d'ensemble Trading
export async function getTradingOverview() {
  const response = await fetch(`${API_BASE_URL}/api/trading/overview`);
  if (!response.ok) throw new Error('Failed to fetch trading overview');
  return response.json();
}

// Signaux de trading
export async function getTradingSignals(signalType?: string, minForce?: number) {
  const params = new URLSearchParams();
  if (signalType) params.append('signal_type', signalType);
  if (minForce) params.append('min_force', minForce.toString());
  
  const url = `${API_BASE_URL}/api/trading/signals${params.toString() ? '?' + params.toString() : ''}`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch trading signals');
  return response.json();
}

// Indicateurs techniques pour un symbole
export async function getTradingIndicators(symbole: string) {
  const response = await fetch(`${API_BASE_URL}/api/trading/indicators/${symbole}`);
  if (!response.ok) throw new Error('Failed to fetch trading indicators');
  return response.json();
}

// Données OHLCV pour graphique
export async function getOHLCVData(symbole: string, limit: number = 90) {
  const response = await fetch(`${API_BASE_URL}/api/trading/ohlcv/${symbole}?limit=${limit}`);
  if (!response.ok) throw new Error('Failed to fetch OHLCV data');
  return response.json();
}

// Heatmap sectorielle
export async function getSectorHeatmap() {
  const response = await fetch(`${API_BASE_URL}/api/trading/heatmap`);
  if (!response.ok) throw new Error('Failed to fetch sector heatmap');
  return response.json();
}

// Top movers
export async function getTopMovers() {
  const response = await fetch(`${API_BASE_URL}/api/trading/movers`);
  if (!response.ok) throw new Error('Failed to fetch top movers');
  return response.json();
}

// Watchlist complète
export async function getTradingWatchlist() {
  const response = await fetch(`${API_BASE_URL}/api/trading/watchlist`);
  if (!response.ok) throw new Error('Failed to fetch trading watchlist');
  return response.json();
}



// ============================================================
// FONCTIONS POUR LA PAGE INVESTISSEMENT
// ============================================================

// Vue d'ensemble Investissement
export async function getInvestmentOverview() {
  const response = await fetch(`${API_BASE_URL}/api/investment/overview`);
  if (!response.ok) throw new Error('Failed to fetch investment overview');
  return response.json();
}

// Screener fondamental
export async function getInvestmentScreener(params?: {
  strategy?: string;
  min_roe?: number;
  max_pe?: number;
  min_div?: number;
  max_debt?: number;
}) {
  const searchParams = new URLSearchParams();
  if (params?.strategy) searchParams.append('strategy', params.strategy);
  if (params?.min_roe) searchParams.append('min_roe', params.min_roe.toString());
  if (params?.max_pe) searchParams.append('max_pe', params.max_pe.toString());
  if (params?.min_div) searchParams.append('min_div', params.min_div.toString());
  if (params?.max_debt) searchParams.append('max_debt', params.max_debt.toString());
  
  const url = `${API_BASE_URL}/api/investment/screener${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch investment screener');
  return response.json();
}

// Données fondamentales pour un symbole
export async function getInvestmentFundamentals(symbole: string) {
  const response = await fetch(`${API_BASE_URL}/api/investment/fundamentals/${symbole}`);
  if (!response.ok) throw new Error('Failed to fetch investment fundamentals');
  return response.json();
}

// Watchlist investissement
export async function getInvestmentWatchlist() {
  const response = await fetch(`${API_BASE_URL}/api/investment/watchlist`);
  if (!response.ok) throw new Error('Failed to fetch investment watchlist');
  return response.json();
}

// ============================================================
// FONCTIONS POUR LA PAGE PRÉDICTIONS ML
// ============================================================

// Vue d'ensemble Prédictions
export async function getPredictionsOverview() {
  const response = await fetch(`${API_BASE_URL}/api/predictions/overview`);
  if (!response.ok) throw new Error('Failed to fetch predictions overview');
  return response.json();
}

// Liste des actions disponibles pour prédictions
export async function getPredictionsList() {
  const response = await fetch(`${API_BASE_URL}/api/predictions/list`);
  if (!response.ok) throw new Error('Failed to fetch predictions list');
  return response.json();
}

// Historique réel d'une action
export async function getPredictionHistory(symbole: string, days: number = 90) {
  const response = await fetch(`${API_BASE_URL}/api/predictions/history/${symbole}?days=${days}`);
  if (!response.ok) throw new Error('Failed to fetch prediction history');
  return response.json();
}

// Prédictions pour une action
export async function getForecast(symbole: string, periods: number = 30) {
  const response = await fetch(`${API_BASE_URL}/api/predictions/forecast/${symbole}?periods=${periods}`);
  if (!response.ok) throw new Error('Failed to fetch forecast');
  return response.json();
}