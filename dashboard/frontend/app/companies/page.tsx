import { fetchCompanies, fetchSectors } from '@/lib/api';
import CompanyList from '@/components/CompanyList';

export default async function CompaniesPage() {
    const companies = await fetchCompanies();
    const sectors = await fetchSectors();

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold">Sociétés Cotées</h1>
            <CompanyList initialCompanies={companies} sectors={sectors} />
        </div>
    )
}
