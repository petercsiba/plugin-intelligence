import {CompaniesTopResponse} from "./models";

const baseUrl = process.env.NEXT_PUBLIC_API_URL

export const fetchTopCompanies = async (): Promise<CompaniesTopResponse[]> => {
    const url = `${baseUrl}/companies/top`
    console.log("Attempting to fetch companies from", url);
    const response = await fetch(url);
    return await response.json();
};
