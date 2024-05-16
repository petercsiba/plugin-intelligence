import {TopPluginResponse} from "./models";


const baseUrl = process.env.NEXT_PUBLIC_API_URL

export const fetchTopPlugins = async (): Promise<TopPluginResponse[]> => {
    const url = `${baseUrl}/plugins/top`
    console.log("Attempting to fetch plugins from", url);
    const response = await fetch(url);
    return await response.json();
};

export const fetchCompanyPlugins = async (companySlug: string): Promise<TopPluginResponse[]> => {
    const url = `${baseUrl}/plugins/company/${companySlug}`
    console.log("Attempting to fetch plugins from", url);
    const response = await fetch(url);
    return await response.json();
};
