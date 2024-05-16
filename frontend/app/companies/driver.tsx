import {CompaniesTopResponse, CompanyDetailsResponse} from "./models";

const baseUrl = process.env.NEXT_PUBLIC_API_URL

export const fetchTopCompanies = async (): Promise<CompaniesTopResponse[]> => {
    const url = `${baseUrl}/companies/top?limit=100`
    console.log("Attempting to fetch companies from", url);
    const response = await fetch(url);
    return await response.json();
};

// Function to fetch company details
export const fetchCompanyDetails = async(company_slug: string): Promise<CompanyDetailsResponse | null> => {
    const response = await fetch(`${baseUrl}/companies/${company_slug}/details`, {
        cache: "no-store", // Adjust caching as needed
    });

    if (!response.ok) {
        console.error(`Error fetching company details: ${response.statusText}`);
        return null;
    }

    return await response.json();
}
