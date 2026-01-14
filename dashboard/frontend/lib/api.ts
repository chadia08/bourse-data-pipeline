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
