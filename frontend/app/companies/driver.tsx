import {CompaniesTopResponse, CompanyDetailsResponse} from "./models";
import {MarketplaceName} from "../marketplaces/models";

const baseUrl = process.env.NEXT_PUBLIC_API_URL

export const fetchTopCompanies = async (marketplaceName: MarketplaceName): Promise<CompaniesTopResponse[]> => {
    const url = `${baseUrl}/companies/top?limit=30&marketplace_name=${marketplaceName}`
    console.log("Attempting to fetch developers from", url);
    const response = await fetch(url);
    return await response.json();
};

// Function to fetch company details
export const fetchCompanyDetails = async(companySlug: string): Promise<CompanyDetailsResponse | null> => {
    const response = await fetch(`${baseUrl}/companies/${companySlug}/details`, {
        cache: "no-store", // Adjust caching as needed
    });

    if (!response.ok) {
        console.error(`Error fetching developer details: ${response.statusText}`);
        return null;
    }

    return await response.json();
}
